/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.roimfs;

import java.io.IOException;
import java.nio.file.ReadOnlyFileSystemException;
import java.nio.file.attribute.BasicFileAttributeView;
import java.nio.file.attribute.BasicFileAttributes;
import java.nio.file.attribute.FileTime;

/**
 * We currently only support the file size and wither its a regular file vs directory.
 * I default to a fixed time, and we don't support modifying the time. As we're a read only system.
 *
 * If someone wants to design and API to store FileTimes then feel free to PR.
 */
class RoimFileAttributeView implements BasicFileAttributeView {
    private static final Attributes DIRECTORY = new Attributes(0, false);

    private final RoimPath path;

    RoimFileAttributeView(RoimPath path) {
        this.path = path;
    }

    @Override
    public String name() {
        return "basic";
    }

    @Override
    public BasicFileAttributes readAttributes() throws IOException {
        String real = path.toRealPath().toString(); // Throws IO Exception on file/directory not found

        if (path.fs.isDirectory(real))
            return DIRECTORY;

        return new Attributes(path.fs.getFile(real).length, true);
    }

    @Override
    public void setTimes(FileTime lastModifiedTime, FileTime lastAccessTime, FileTime createTime) throws IOException {
        throw new ReadOnlyFileSystemException();
    }

    static class Attributes implements BasicFileAttributes {
        private static final FileTime TIME = FileTime.fromMillis(0x923BE9C000L);

        private final long size;
        private final boolean isFile;

        Attributes(long size, boolean isFile) {
            this.size = size;
            this.isFile = isFile;
        }

        @Override
        public long size() {
            return size;
        }

        @Override
        public boolean isRegularFile() {
            return isFile;
        }

        @Override
        public boolean isDirectory() {
            return !isRegularFile();
        }

        @Override
        public FileTime lastModifiedTime() {
            return TIME;
        }

        @Override
        public FileTime lastAccessTime() {
            return TIME;
        }

        @Override
        public FileTime creationTime() {
            return TIME;
        }

        @Override
        public boolean isSymbolicLink() {
            return false;
        }

        @Override
        public boolean isOther() {
            return false;
        }

        @Override
        public Object fileKey() {
            return null;
        }
    }
}
