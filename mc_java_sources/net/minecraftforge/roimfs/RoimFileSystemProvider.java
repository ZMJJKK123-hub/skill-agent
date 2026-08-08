/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.roimfs;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URI;
import java.nio.channels.AsynchronousFileChannel;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.AccessDeniedException;
import java.nio.file.AccessMode;
import java.nio.file.CopyOption;
import java.nio.file.DirectoryStream;
import java.nio.file.DirectoryStream.Filter;
import java.nio.file.FileStore;
import java.nio.file.FileSystem;
import java.nio.file.FileSystemAlreadyExistsException;
import java.nio.file.FileSystemException;
import java.nio.file.FileSystemNotFoundException;
import java.nio.file.LinkOption;
import java.nio.file.OpenOption;
import java.nio.file.Path;
import java.nio.file.ProviderMismatchException;
import java.nio.file.ReadOnlyFileSystemException;
import java.nio.file.StandardOpenOption;
import java.nio.file.attribute.BasicFileAttributeView;
import java.nio.file.attribute.BasicFileAttributes;
import java.nio.file.attribute.FileAttribute;
import java.nio.file.attribute.FileAttributeView;
import java.nio.file.spi.FileSystemProvider;
import java.util.HashMap;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ExecutorService;

public final class RoimFileSystemProvider extends FileSystemProvider {
    static final String SCHEMA = "roimfs";
    private final Map<String, RoimFileSystem> filesystems = new HashMap<>();

    @Override
    public String getScheme() {
        return SCHEMA;
    }

    /* The main thing we're concerned about is the schema and path, everything else needs to be empty
     * The path must contain the 'key' for the target file system.
     * The 'key' is an arbitrary String, not containing a /, that is used when first creating the FileSystem.
     * Consumers are meant to manage the uniqueness of this key themselves.
     *
     * Expected format is:
     *   roimfs:key/some/path
     *
     */
    private void checkUri(URI uri) {
        if (!uri.getScheme().equalsIgnoreCase(getScheme()))
            throw new IllegalArgumentException("URI does not match this provider");
        if (uri.getRawAuthority() != null)
            throw new IllegalArgumentException("Authority component present");
        if (uri.getRawQuery() != null)
            throw new IllegalArgumentException("Query component present");
        if (uri.getRawFragment() != null)
            throw new IllegalArgumentException("Fragment component present");
        String path = uri.getSchemeSpecificPart();
        if (path == null)
            throw new IllegalArgumentException("Path component is undefined");
        int idx = path.indexOf('/');
        if (idx == -1 || idx == 0)
            throw new IllegalArgumentException("Path must contain a key");
    }

    @Override
    public FileSystem newFileSystem(URI uri, Map<String, ?> env) throws IOException {
        checkUri(uri);

        // Register URL handler if we need to
        Handler.register();

        String raw = uri.getSchemeSpecificPart();
        int idx = raw.indexOf('/');
        String key = raw.substring(0, idx);
        String path = raw.substring(idx + 1);

        synchronized (filesystems) {
            if (filesystems.containsKey(key))
                throw new FileSystemAlreadyExistsException();

            RoimFileSystem fs = new RoimFileSystem(this, key, path, env);
            filesystems.put(key, fs);
            return fs;
        }
    }

    @Override
    public FileSystem getFileSystem(URI uri) {
        checkUri(uri);

        String path = uri.getSchemeSpecificPart();
        int idx = path.indexOf('/');
        String key = path.substring(0, idx);

        synchronized (filesystems){
            FileSystem fs = filesystems.get(key);
            if (fs == null)
                throw new FileSystemNotFoundException();
            return fs;
        }
    }

    void removeFileSystem(RoimFileSystem fs) {
        synchronized (filesystems) {
            filesystems.remove(fs.getKey());
        }
    }

    @Override
    public Path getPath(URI uri) {
        checkUri(uri);
        int idx = uri.getRawSchemeSpecificPart().indexOf('/');
        String path = uri.getRawSchemeSpecificPart().substring(idx + 1);
        return getFileSystem(uri).getPath(path);
    }

    private static RoimPath cast(Path path) {
        if (path == null)
            throw new NullPointerException();
        if (!(path instanceof RoimPath))
            throw new ProviderMismatchException();
        return (RoimPath)path;
    }

    private static RoimFileSystem getFileSystem(Path path) {
        return (RoimFileSystem)cast(path).getFileSystem();
    }

    @Override
    public SeekableByteChannel newByteChannel(Path path, Set<? extends OpenOption> options, FileAttribute<?>... attrs) throws IOException {
        for (OpenOption option : options) {
            if (option != StandardOpenOption.READ)
                throw new UnsupportedOperationException("'" + option + "' not allowed");
        }

        RoimFileSystem fs = getFileSystem(path);
        String str = path.toRealPath().toString();
        if (fs.isDirectory(str))
            throw new FileSystemException(RoimFileSystemProvider.SCHEMA + ':' + fs.getKey() +  path + " is a directory");
        byte[] data = getFileSystem(path).getFile(str);
        return new ReadOnlyByteChannel(data);
    }

    @Override
    public InputStream newInputStream(Path path, OpenOption... options) throws IOException {
        for (OpenOption option : options) {
            if (option != StandardOpenOption.READ)
                throw new UnsupportedOperationException("'" + option + "' not allowed");
        }
        RoimFileSystem fs = getFileSystem(path);
        String str = path.toRealPath().toString();
        if (fs.isDirectory(str))
            throw new FileSystemException(RoimFileSystemProvider.SCHEMA + ':' + fs.getKey() +  path + " is a directory");
        byte[] data = getFileSystem(path).getFile(str);
        return new ByteArrayInputStream(data);
    }

    // TODO: [ROIMFS] newFileChannel - Not strictly necessary, but could be done eventually
    @Override
    public FileChannel newFileChannel(Path path, Set<? extends OpenOption> options, FileAttribute<?>... attrs) throws IOException {
        throw new UnsupportedOperationException();
    }

    // TODO: [ROIMFS] newAsynchronousFileChannel - Not strictly necessary, but could be done eventually
    @Override
    public AsynchronousFileChannel newAsynchronousFileChannel(Path path, Set<? extends OpenOption> options, ExecutorService executor, FileAttribute<?>... attrs) throws IOException {
        throw new UnsupportedOperationException();
    }

    @Override
    public DirectoryStream<Path> newDirectoryStream(Path dir, Filter<? super Path> filter) throws IOException {
        return getFileSystem(dir).newDirectoryStream(dir, filter);
    }

    @Override
    public boolean isSameFile(Path path, Path other) throws IOException {
        if (path.equals(other))
            return true;

        if (other == null || path.getFileSystem() != other.getFileSystem())
            return false;

        Path realA = path.toRealPath();
        Path realB = other.toRealPath();
        return realA.equals(realB);
    }

    @Override
    public boolean isHidden(Path path) throws IOException {
        return false;
    }

    @Override
    public FileStore getFileStore(Path path) throws IOException {
        return getFileSystem(path).getFileStore();
    }

    @Override
    public void checkAccess(Path path, AccessMode... modes) throws IOException {
        RoimPath rPath = cast(path);
        for (AccessMode mode : modes) {
            if (mode != AccessMode.READ)
                throw new AccessDeniedException(rPath.toString());
        }
    }


    @SuppressWarnings("unchecked")
    @Override
    public <V extends FileAttributeView> V getFileAttributeView(Path path, Class<V> type, LinkOption... options) {
        if (type == null)
            throw new NullPointerException();

        if (type == BasicFileAttributeView.class)
            return (V)new RoimFileAttributeView(cast(path));

        return null;
    }

    @SuppressWarnings("unchecked")
    @Override
    public <A extends BasicFileAttributes> A readAttributes(Path path, Class<A> type, LinkOption... options) throws IOException {
        if (type != BasicFileAttributes.class)
            throw new UnsupportedOperationException("Attribute type " + type.getName() + " is not supported");

        return (A)getFileAttributeView(path, BasicFileAttributeView.class, options).readAttributes();
    }

    @Override
    public Map<String, Object> readAttributes(Path path, String attributes, LinkOption... options) throws IOException {
        String type;
        String attrs;
        int idx = attributes.indexOf(':');
        if (idx == -1) {
            type = "basic";
            attrs = attributes;
        } else {
            type = attributes.substring(0, idx);
            attrs = attributes.substring(idx + 1);
        }

        if (!"basic".equals(type))
            throw new UnsupportedOperationException("View type `" + type + "` is not supported");

        Map<String, Object> ret = new HashMap<>();
        BasicFileAttributes view = getFileAttributeView(path, BasicFileAttributeView.class, options).readAttributes();
        for (String name : attrs.split(",")) {
            switch (name) {
                case "*":
                    ret.put("size",             view.size());
                    ret.put("creationTime",     view.creationTime());
                    ret.put("lastAccessTime",   view.lastAccessTime());
                    ret.put("lastModifiedTime", view.lastModifiedTime());
                    ret.put("isDirectory",      view.isDirectory());
                    ret.put("isRegularFile",    view.isRegularFile());
                    ret.put("isSymbolicLink",   view.isSymbolicLink());
                    ret.put("isOther",          view.isOther());
                    ret.put("fileKey",          view.fileKey());
                    break;
                case "size":             ret.put("size",             view.size());             break;
                case "creationTime":     ret.put("creationTime",     view.creationTime());     break;
                case "lastAccessTime":   ret.put("lastAccessTime",   view.lastAccessTime());   break;
                case "lastModifiedTime": ret.put("lastModifiedTime", view.lastModifiedTime()); break;
                case "isDirectory":      ret.put("isDirectory",      view.isDirectory());      break;
                case "isRegularFile":    ret.put("isRegularFile",    view.isRegularFile());    break;
                case "isSymbolicLink":   ret.put("isSymbolicLink",   view.isSymbolicLink());   break;
                case "isOther":          ret.put("isOther",          view.isOther());          break;
                case "fileKey":          ret.put("fileKey",          view.fileKey());          break;
            }
        }
        return ret;
    }

    // Modification operations, throw ReadOnlyFileSystemException
    @Override
    public void createDirectory(Path dir, FileAttribute<?>... attrs) throws IOException {
        throw new ReadOnlyFileSystemException();
    }

    @Override
    public void delete(Path path) throws IOException {
        throw new ReadOnlyFileSystemException();
    }

    @Override
    public void copy(Path source, Path target, CopyOption... options) throws IOException {
        throw new ReadOnlyFileSystemException();
    }

    @Override
    public void move(Path source, Path target, CopyOption... options) throws IOException {
        throw new ReadOnlyFileSystemException();
    }

    @Override
    public void setAttribute(Path path, String attribute, Object value, LinkOption... options) throws IOException {
        throw new ReadOnlyFileSystemException();
    }

    @Override
    public OutputStream newOutputStream(Path path, OpenOption... options) throws IOException {
        throw new ReadOnlyFileSystemException();
    }

    @Override
    public void createSymbolicLink(Path link, Path target, FileAttribute<?>... attrs) throws IOException {
        throw new ReadOnlyFileSystemException();
    }
}
