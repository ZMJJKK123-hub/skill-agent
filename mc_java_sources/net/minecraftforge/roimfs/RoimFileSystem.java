/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.roimfs;

import java.io.IOException;
import java.nio.file.DirectoryStream;
import java.nio.file.DirectoryStream.Filter;
import java.nio.file.FileStore;
import java.nio.file.FileSystem;
import java.nio.file.NoSuchFileException;
import java.nio.file.NotDirectoryException;
import java.nio.file.Path;
import java.nio.file.PathMatcher;
import java.nio.file.WatchService;
import java.nio.file.attribute.UserPrincipalLookupService;
import java.nio.file.spi.FileSystemProvider;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Map.Entry;
import java.util.Set;
import java.util.regex.Pattern;

final class RoimFileSystem extends FileSystem {
    private static final byte[] EMPTY = new byte[0];
    final RoimPath rootPath = new RoimPath(this, new char[]{ '/' }, true);
    private final String key;

    private final Set<String> directories = new HashSet<>();
    private final RoimFileSystemProvider provider;
    private final Map<String, byte[]> files;
    private final RoimFileStore fileStore;

    private boolean isOpen = true;

    RoimFileSystem(RoimFileSystemProvider provider, String key, String path, Map<String, ?> env) {
        this.provider = provider;
        this.key = key;

        int total = 0;

        if (!path.isEmpty()) {
            path = normalize(path);
            if (path.endsWith("/")) {
                this.directories.add(path);
                this.files = Collections.emptyMap();
            } else {
                byte[] data = (byte[])env.get("data");
                if (data == null)
                    throw new IllegalArgumentException("Must specify `data` value when specifying path in constructor");

                this.files = Collections.singletonMap(path, data);
                addParents(path);
                total += data.length;
            }
        } else {
            @SuppressWarnings("unchecked")
            Map<String, byte[]> data = (Map<String, byte[]>)env.get("files");
            if (data == null)
                throw new IllegalArgumentException("Must specify `files` value which is a Map<String, byte[]>");

            this.files = new HashMap<>();
            for (Entry<String, byte[]> file : data.entrySet()) {
                String name = normalize(file.getKey());

                addParents(name);

                if (!name.endsWith("/")) {
                    byte[] fdata = file.getValue() == null ? EMPTY : file.getValue();
                    total += fdata.length;
                    files.put(name, fdata);
                }
            }
        }

        // Make sure they didn't make a directory that is also a file.
        // ZipFileSystem doesn't allow making paths with a trailing / so there isn't a good way to explicitly request it
        // Need to look more into this and test with ZipFiles
        for (String file : files.keySet()) {
            if (directories.contains(file + '/'))
                throw new IllegalArgumentException("Can not create a file, and directory with the same name: " + file);
        }

        this.fileStore = new RoimFileStore(total);
    }

    private static String normalize(String path) {
        return path.length() == 0 ? "/" : path.charAt(0) == '/' ? path : '/' + path;
    }

    private void addParents(String path) {
        int idx = path.lastIndexOf('/');
        while (idx != -1) {
            directories.add(path.substring(0, idx + 1));
            idx = path.lastIndexOf('/', idx - 1);
        }
    }

    String getKey() {
        return this.key;
    }

    void checkExists(String path) throws NoSuchFileException {
        if (!files.containsKey(path) && !isDirectory(path))
            throw new NoSuchFileException(RoimFileSystemProvider.SCHEMA + ':' + this.key +  path);
    }

    byte[] getFile(String path) throws NoSuchFileException {
        byte[] ret = files.get(path);
        if (ret == null)
            throw new NoSuchFileException(RoimFileSystemProvider.SCHEMA + ':' + this.key +  path);
        return ret;
    }

    boolean isDirectory(String path) {
        return directories.contains(path) || directories.contains(path + '/');
    }

    @Override
    public String toString() {
        return RoimFileSystemProvider.SCHEMA + ':' + getKey() + ' ' + this.files.keySet();
    }

    @Override
    public FileSystemProvider provider() {
        return this.provider;
    }

    @Override
    public boolean isOpen() {
        return isOpen;
    }

    @Override
    public boolean isReadOnly() {
        return true;
    }

    @Override
    public String getSeparator() {
        return "/";
    }

    @Override
    public Iterable<Path> getRootDirectories() {
        return Arrays.asList(rootPath);
    }

    @Override
    public Iterable<FileStore> getFileStores() {
        return Arrays.asList(fileStore);
    }

    FileStore getFileStore() {
        return this.fileStore;
    }

    DirectoryStream<Path> newDirectoryStream(Path dir, Filter<? super Path> filter) throws IOException {
        Path real = dir.toAbsolutePath().normalize();
        String str = real.toString();
        if (str.charAt(str.length() - 1) != '/')
            str += '/';

        if (!this.directories.contains(str))
            throw new NotDirectoryException(str);

        int dlen = str.length();

        List<Path> ret = new ArrayList<>();
        for (String file : files.keySet()) {
            // Does it start with our path?
            if (file.length() < dlen
                || !file.startsWith(str)
                || file.indexOf('/', dlen + 1) != -1)
                continue;
            String name = file.substring(dlen);
            ret.add(dir.resolve(name));
        }

        for (String other : directories) {
            if (other.length() <= dlen || !other.startsWith(str))
                continue;
            int idx = other.indexOf('/', dlen + 1);
            if (idx != other.length() - 1) // we only want direct children
                continue;
            String name = other.substring(dlen, idx + 1);
            ret.add(dir.resolve(name));
        }

        Collections.sort(ret);
        return new RoimDirectoryStream(ret, filter);
    }

    private static final Set<String> supportedFileAttributeViews = Collections.singleton("basic");
    @Override
    public Set<String> supportedFileAttributeViews() {
        return supportedFileAttributeViews;
    }


    @Override
    public void close() throws IOException {
        // TODO Auto-generated method stub
        this.provider.removeFileSystem(this);
    }

    @Override
    public Path getPath(String first, String... more) {
        if (more.length == 0)
            return new RoimPath(this, first);

        StringBuilder sb = new StringBuilder();
        sb.append(first);
        for (String part : more) {
            if (part.length() == 0)
                continue;
            if (sb.length() > 0)
                sb.append('/');
            sb.append(part);
        }

        return new RoimPath(this, sb.toString());
    }

    @Override
    public PathMatcher getPathMatcher(String syntaxAndPattern) {
        int pos = syntaxAndPattern.indexOf(':');
        if (pos <= 0)
            throw new IllegalArgumentException();

        String syntax = syntaxAndPattern.substring(0, pos);
        String pattern = syntaxAndPattern.substring(pos + 1);
        String expr;
        if (syntax.equalsIgnoreCase("glob"))
            expr = GlobUtil.convertGlobToRegex(pattern);
        else if (syntax.equalsIgnoreCase("regex"))
            expr = pattern;
        else
            throw new UnsupportedOperationException("Syntax '" + syntax + "' not recognized");

        // return matcher
        final Pattern regex = Pattern.compile(expr);
        return path -> regex.matcher(path.toString()).matches();
    }

    // Yay things we don't have to implement!
    @Override
    public UserPrincipalLookupService getUserPrincipalLookupService() {
        throw new UnsupportedOperationException();
    }

    @Override
    public WatchService newWatchService() throws IOException {
        throw new UnsupportedOperationException();
    }
}
