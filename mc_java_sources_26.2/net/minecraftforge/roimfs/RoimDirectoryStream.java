/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.roimfs;

import java.io.IOException;
import java.nio.file.ClosedDirectoryStreamException;
import java.nio.file.DirectoryIteratorException;
import java.nio.file.DirectoryStream;
import java.nio.file.Path;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;

class RoimDirectoryStream implements DirectoryStream<Path> {
    private final List<Path> files;
    private final Filter<? super Path> filter;
    private volatile boolean isClosed;
    private volatile Iterator<Path> itr;

    RoimDirectoryStream(List<Path> files, Filter<? super Path> filter) {
        this.files = files;
        this.filter = filter;
    }

    @Override
    public void close() throws IOException {
        isClosed = true;
        files.clear();
    }

    @Override
    public Iterator<Path> iterator() {
        if (isClosed)
            throw new ClosedDirectoryStreamException();

        if (itr != null)
            throw new IllegalStateException("Iterator has already been returned");

        itr = files.iterator();

        return new Iterator<Path>() {
            private Path next = null;

            @Override
            public boolean hasNext() {
                if (isClosed)
                    return false;

                while (itr.hasNext()) {
                    next = itr.next();
                    try {
                        if (filter == null || filter.accept(next))
                            break;
                        else
                            next = null;
                    } catch (IOException e) {
                        throw new DirectoryIteratorException(e);
                    }
                }

                return next != null;
            }

            @Override
            public Path next() {
                if (isClosed || next == null)
                    throw new NoSuchElementException();

                Path ret = next;
                next = null;
                return ret;
            }

            @Override
            public void remove() {
                throw new UnsupportedOperationException();
            }
        };
    }

}
