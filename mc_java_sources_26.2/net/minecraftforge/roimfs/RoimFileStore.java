/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.roimfs;

import java.io.IOException;
import java.nio.file.FileStore;
import java.nio.file.attribute.BasicFileAttributeView;
import java.nio.file.attribute.FileAttributeView;
import java.nio.file.attribute.FileStoreAttributeView;

final class RoimFileStore extends FileStore {
    private final int totalSize;

    RoimFileStore(int totalSize) {
        this.totalSize = totalSize;
    }

    @Override
    public String name() {
        return RoimFileSystemProvider.SCHEMA;
    }

    @Override
    public String type() {
        return RoimFileSystemProvider.SCHEMA;
    }

    @Override
    public boolean isReadOnly() {
        return true;
    }

    @Override
    public long getTotalSpace() throws IOException {
        return this.totalSize;
    }

    @Override
    public long getUsableSpace() throws IOException {
        return this.totalSize;
    }

    @Override
    public long getUnallocatedSpace() throws IOException {
        return 0;
    }

    @Override
    public boolean supportsFileAttributeView(Class<? extends FileAttributeView> type) {
        return type == BasicFileAttributeView.class;
    }

    @Override
    public boolean supportsFileAttributeView(String name) {
        return "basic".equals(name);
    }

    @Override
    public <V extends FileStoreAttributeView> V getFileStoreAttributeView(Class<V> type) {
        return null; // All known jdk implementations return null
    }

    @Override
    public Object getAttribute(String attribute) throws IOException {
        if ("totalSpace".equals(attribute))
            return getTotalSpace();
        if ("usableSpace".equals(attribute))
            return getUsableSpace();
        if ("unallocatedSpace".equals(attribute))
            return getUnallocatedSpace();
        throw new UnsupportedOperationException("does not support the given attribute: " + attribute);
    }
}
