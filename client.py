#! /usr/bin/env python

from __future__ import absolute_import, division, print_function

import Queue
import cv2
import json
import logging
import select
import struct
import threading
import time
from base64 import b64decode
from time import sleep

import fire
import logzero
import numpy as np
from logzero import logger

import protocol
from config import Config
from socketLib import ClientCommand, ClientReply, SocketClientThread


class GabrielSocketCommand(ClientCommand):
    STREAM = len(ClientCommand.ACTIONS)
    ACTIONS = ClientCommand.ACTIONS + [STREAM]
    LISTEN = len(ACTIONS)
    ACTIONS.append(LISTEN)

    def __init__(self, type, data=None):
        super(GabrielSocketCommand, self).__init__()


class VideoCaptureThread(threading.Thread):
    """
    Thread tasked with capturing video from the camera at a fixed rate.
    """

    def __init__(self,
                 input_source,
                 fps=24,
                 sig_feed_available=None):
        super(VideoCaptureThread, self).__init__()
        self.input_source = input_source
        self.sig_feed = sig_feed_available
        self.alive = threading.Event()
        self.alive.set()
        self.frame_buf = Queue.Queue(maxsize=1)  # holds latest frame
        self.interval = 1.0 / float(fps)
        self.daemon = True

    def run(self):
        video_capture = cv2.VideoCapture(self.input_source)
        while self.alive.isSet():
            ti = time.time()
            ret, frame = video_capture.read()

            if ret:
                if self.sig_feed:
                    self.sig_feed.emit(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                self._put_frame((ret, frame))
                time.sleep(max(self.interval - (time.time() - ti), 0))
            else:
                logger.debug(
                    'No more video frames from {}'.format(self.input_source))

                self._put_frame((ret, None))
                break

        video_capture.release()

    def _put_frame(self, frame):
        while True:
            try:
                self.frame_buf.put(frame, block=False)
                return
            except Queue.Full:
                self.frame_buf.get()

    def get_frame(self):
        return self.frame_buf.get(block=True)

    def join(self, timeout=None):
        self.alive.clear()
        threading.Thread.join(self, timeout)


class VideoStreamingThread(SocketClientThread):
    def __init__(self, video_capture,
                 cmd_q=None, reply_q=None):
        super(VideoStreamingThread, self).__init__(cmd_q, reply_q)
        self.handlers[GabrielSocketCommand.STREAM] = self._handle_STREAM
        self.is_streaming = False
        self.video_capture = video_capture

    def run(self):
        while self.alive.isSet():
            try:
                cmd = self.cmd_q.get(True, 0.1)
                self.handlers[cmd.type](cmd)
            except Queue.Empty as e:
                continue

    # tokenm: token manager
    def _handle_STREAM(self, cmd):
        tokenm = cmd.data
        self.is_streaming = True
        id = 0
        while self.alive.isSet() and self.is_streaming:
            # will be put into sleep if token is not available
            tokenm.getToken()
            ret, frame = self.video_capture.get_frame()
            if not ret:
                break
            ret, jpeg_frame = cv2.imencode('.jpg', frame)
            header = {protocol.Protocol_client.JSON_KEY_FRAME_ID: str(id)}
            header_json = json.dumps(header)
            self._handle_SEND(ClientCommand(ClientCommand.SEND, header_json))
            self._handle_SEND(ClientCommand(
                ClientCommand.SEND, jpeg_frame.tostring()))
            logger.debug('Send Frame {}'.format(id))
            id += 1


class ResultReceivingThread(SocketClientThread):
    def __init__(self, cmd_q=None, reply_q=None, legacy=Config.LEGACY):
        super(ResultReceivingThread, self).__init__(cmd_q, reply_q)
        self.handlers[GabrielSocketCommand.LISTEN] = self._handle_LISTEN
        self.is_listening = False
        self.legacy = legacy

    def run(self):
        while self.alive.isSet():
            try:
                cmd = self.cmd_q.get(True, 0.1)
                self.handlers[cmd.type](cmd)
            except Queue.Empty as e:
                continue

    def _handle_LISTEN(self, cmd):
        tokenm = cmd.data
        self.is_listening = True
        while self.alive.isSet() and self.is_listening:
            if self.socket:
                input = [self.socket]
                inputready, outputready, exceptready = select.select(
                    input, [], [])
                for s in inputready:
                    if s == self.socket:
                        # handle the server socket
                        header, data = self._recv_gabriel_data()
                        self.reply_q.put(self._success_reply((header, data)))
                        tokenm.putToken()

    def _recv_gabriel_data(self):
        header_size = struct.unpack("!I", self._recv_n_bytes(4))[0]
        header = self._recv_n_bytes(header_size)
        header_json = json.loads(header)
        if self.legacy:
            data = header_json.pop('result')
        else:
            data_size = header_json['data_size']
            data = self._recv_n_bytes(data_size)
        return (header, data)


class TokenManager(object):
    """Implements Gabriel's token mechanism."""

    def __init__(self, token_num):
        super(TokenManager, self).__init__()
        self.token_num = token_num
        # token val is [0..token_num)
        self.token_val = token_num - 1
        self.lock = threading.Lock()
        self.has_token_cv = threading.Condition(self.lock)

    def _inc(self):
        self.token_val = (self.token_val + 1) if (self.token_val <
                                                  self.token_num) else (
            self.token_val)

    def _dec(self):
        self.token_val = (
                self.token_val - 1) if (self.token_val >= 0) else (
            self.token_val)

    def empty(self):
        return (self.token_val < 0)

    def getToken(self):
        with self.has_token_cv:
            while self.token_val < 0:
                self.has_token_cv.wait()
            self._dec()

    def putToken(self):
        with self.has_token_cv:
            self._inc()
            if self.token_val >= 0:
                self.has_token_cv.notifyAll()


def parse(data):
    if Config.LEGACY:
        return json.loads(data)
    else:
        return data


def create_video_threads(video_input, sig_feed_available):
    stream_cmd_q = Queue.Queue()
    video_capture_thread = VideoCaptureThread(video_input,
                                              sig_feed_available=sig_feed_available)
    video_streaming_thread = VideoStreamingThread(video_capture_thread,
                                                  cmd_q=stream_cmd_q)
    video_streaming_thread.daemon = True
    return video_capture_thread, video_streaming_thread, stream_cmd_q


def create_receiving_thread(legacy):
    result_cmd_q = Queue.Queue()
    result_reply_q = Queue.Queue()
    result_receiving_thread = ResultReceivingThread(
        cmd_q=result_cmd_q, reply_q=result_reply_q, legacy=legacy)
    result_receiving_thread.daemon = True
    return result_receiving_thread, result_cmd_q, result_reply_q


def run(sig_feed_available=None,
        sig_instruction_available=None,
        sig_guidance_available=None,
        video_input=0,
        ip=Config.GABRIEL_IP,
        video_port=Config.VIDEO_STREAM_PORT,
        result_port=Config.RESULT_RECEIVING_PORT,
        legacy=Config.LEGACY):
    logger.debug(
        "Connecting to Server ({}) Port ({}, {})".format(ip, video_port,
                                                         result_port))
    tokenm = TokenManager(Config.TOKEN)

    video_capture_thread, \
    video_streaming_thread, \
    stream_cmd_q = create_video_threads(video_input, sig_feed_available)
    # connect and stream to server
    stream_cmd_q.put(ClientCommand(ClientCommand.CONNECT,
                                   (ip, video_port)))
    stream_cmd_q.put(ClientCommand(GabrielSocketCommand.STREAM, tokenm))
    # connect and listen to server
    result_receiving_thread, result_cmd_q, result_reply_q = \
        create_receiving_thread(
            legacy=legacy)
    result_cmd_q.put(ClientCommand(ClientCommand.CONNECT,
                                   (ip, result_port)))
    result_cmd_q.put(ClientCommand(GabrielSocketCommand.LISTEN, tokenm))

    video_capture_thread.start()

    result_receiving_thread.start()
    sleep(0.1)
    video_streaming_thread.start()

    def join_threads():
        video_streaming_thread.join()
        result_receiving_thread.join()
        video_capture_thread.join()
        with tokenm.has_token_cv:
            tokenm.has_token_cv.notifyAll()

    try:
        while True:
            resp = result_reply_q.get()
            # connect and send also send reply to reply queue without any
            # data attached
            if resp.type == ClientReply.SUCCESS and resp.data is not None:
                (resp_header, resp_data) = resp.data
                resp_header = json.loads(resp_header)
                logger.debug('header: {}'.format(resp_header))
                resp_dict = parse(resp_data)

                instruction = resp_dict.get('speech', False)
                if instruction and len(instruction) > 0:
                    logger.info('instruction: {}'.format(instruction))
                    if sig_instruction_available:
                        sig_instruction_available.emit(instruction)

                guidance = False
                animation_frames = resp_dict.get('animation', [])
                if len(animation_frames) > 0 and \
                        len(animation_frames[-1]) > 0:
                    guidance = b64decode(animation_frames[-1][0])

                if sig_guidance_available and guidance and \
                        len(guidance) > 0:
                    np_data = np.fromstring(guidance, dtype=np.uint8)
                    frame = cv2.imdecode(np_data, cv2.CV_LOAD_IMAGE_COLOR)
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    sig_guidance_available.emit(rgb_frame)

            elif resp.type == ClientReply.ERROR:
                logger.error("Error: {}".format(resp.data))
                join_threads()
                break
    except KeyboardInterrupt:
        join_threads()


if __name__ == '__main__':
    logzero.loglevel(logging.INFO)
    fire.Fire(run)
