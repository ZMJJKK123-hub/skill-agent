/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.roimfs;

import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.channels.ClosedChannelException;
import java.nio.channels.NonWritableChannelException;
import java.nio.channels.SeekableByteChannel;

class ReadOnlyByteChannel implements SeekableByteChannel {
    private final byte[] data;
    private boolean isOpen = true;
    private int position = 0;

    ReadOnlyByteChannel(byte[] data) {
        this.data = data;
    }

    private void ensureOpen() throws IOException {
        if (!isOpen)
            throw new ClosedChannelException();
    }

    @Override
    public boolean isOpen() {
        return isOpen;
    }

    @Override
    public void close() throws IOException {
        isOpen = false;
    }

    @Override
    public long position() throws IOException {
        ensureOpen();
        return position;
    }

    @Override
    public SeekableByteChannel position(long newPosition) throws IOException {
        if (newPosition < 0)
            throw new IllegalArgumentException("newPosition is negative: " + newPosition);
        if (newPosition > Integer.MAX_VALUE) // ByteBuffer only works in ints, and really, don't think we should support more.
            throw new IllegalArgumentException("newPosition is larger then Integer.MAX_VALUE");
        ensureOpen();
        this.position = (int)newPosition;
        if (newPosition > data.length)
            this.position = data.length;
        return this;
    }

    @Override
    public long size() throws IOException {
        ensureOpen();
        return data.length;
    }

    @Override
    public int read(ByteBuffer dst) throws IOException {
        synchronized (data) {
            ensureOpen();
            if (position > data.length)
                return -1;
            int count = dst.remaining();
            if (count > data.length - position)
                count = data.length - position;
            if (count > 0) {
	            dst.put(data, position, count);
	            if (count != -1)
	            	position += count;
            }
            return count;
        }
    }

    @Override
    public int write(ByteBuffer src) throws IOException {
        throw new NonWritableChannelException();
    }

    @Override
    public SeekableByteChannel truncate(long size) throws IOException {
        throw new NonWritableChannelException();
    }
}
