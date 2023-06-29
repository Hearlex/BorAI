from whispercpp import Whisper
import discord
import wave
import socket
import select
import asyncio
import threading
import numpy as np
from time import sleep

class VoiceModule():
    def __init__(self, bot):
        self.bot = bot
        self.connections = {}
        self.decoder = None
        self.stt = Whisper.from_pretrained("large")
        self.stt.params.with_language("hu")
        
        self.f = None
        self.data = np.zeros(shape=(0))
        
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You are not connected to a voice channel")
            return
        channel = ctx.author.voice.channel
        vc = await channel.connect()
        self.connections.update({ctx.guild.id: vc})
        
        await ctx.respond("Joined voice channel")
        
    async def leave(self, ctx):
        await self.connections[ctx.guild.id].disconnect()
        await ctx.respond("Left voice channel")
    
    async def record(self, ctx):
        vc = self.connections[ctx.guild.id]
        self.connections[f'{ctx.guild.id}isRec'] = True
        self.decoder = discord.opus.DecodeManager(self)
        self.decoder.start()
        await ctx.respond(vc.socket)
        self.f = wave.open("test.wav", "wb")
        self.f.setnchannels(self.decoder.CHANNELS)
        self.f.setsampwidth(self.decoder.SAMPLE_SIZE // self.decoder.CHANNELS)
        self.f.setframerate(self.decoder.SAMPLING_RATE)
        threading.Thread(
            target=self.recv_audio,
            args=(vc,ctx)
        ).start()
        threading.Thread(
            target=self.transcribe,
            args=(ctx,)
        ).start()
    
    def recv_audio(self, vc, ctx):
        while self.connections[f'{ctx.guild.id}isRec']:
            ready, _, err = select.select([vc.socket], [], [vc.socket], 0.01)
            if not ready:
                if err:
                    print(f'Error: {err}')
                continue
            
            try:
                data = vc.socket.recv(1024)
            except OSError:
                print('Error: OSError')
                self.stopRecording(ctx)
                continue
            
            self.unpack_audio(data, vc)
    
    def recv_decoded_audio(self, data):
        dec_data = data.decoded_data
        if dec_data is not None:
            self.f.writeframes(dec_data)
            y = np.frombuffer(data, np.int16).flatten().astype(np.float32) / 32768.0
            self.data = np.concatenate((self.data, y))
    
    # This is a modified version of the original function from pycord
    def unpack_audio(self, data, vc):
        """Takes an audio packet received from Discord and decodes it into pcm audio data.
        If there are no users talking in the channel, `None` will be returned.

        You must be connected to receive audio.

        .. versionadded:: 2.0

        Parameters
        ----------
        data: :class:`bytes`
            Bytes received by Discord via the UDP connection used for sending and receiving voice data.
        """
        if 200 <= data[1] <= 204:
            # RTCP received.
            # RTCP provides information about the connection
            # as opposed to actual audio data, so it's not
            # important at the moment.
            return

        data = discord.sinks.RawData(data, vc)

        if data.decrypted_data == b"\xf8\xff\xfe":  # Frame of silence
            return

        self.decoder.decode(data)
    
    async def stopRecording(self, ctx):
        self.connections[f'{ctx.guild.id}isRec'] = False
        self.decoder.stop()
        await ctx.respond("Stopped recording")
        self.f.close()
    
    def transcribe(self, ctx):
        timer = 0
        while self.connections[f'{ctx.guild.id}isRec']:
            sleep(1)
            if timer % 3 == 0:
                print(self.stt.transcribe(self.data))
            timer += 1
        print(self.data)
            