/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.roimfs;

import java.io.File;
import java.io.IOException;
import java.net.URI;
import java.net.URISyntaxException;
import java.nio.file.FileSystem;
import java.nio.file.LinkOption;
import java.nio.file.Path;
import java.nio.file.ProviderMismatchException;
import java.nio.file.ReadOnlyFileSystemException;
import java.nio.file.WatchEvent;
import java.nio.file.WatchEvent.Kind;
import java.nio.file.WatchEvent.Modifier;
import java.nio.file.WatchKey;
import java.nio.file.WatchService;
import java.util.Arrays;
import java.util.Iterator;
import java.util.NoSuchElementException;

class RoimPath implements Path {
    final RoimFileSystem fs;
    private final char[] path;

    // Lazy stuff
    private int[] offsets = null;
    private int hashcode = 0;
    // Path with navigations (. and ..) removed
    private Path normalized = null;
    // Absolute Normalized path
    private RoimPath resolved = null;

    RoimPath(RoimFileSystem fs, String path) {
        this(fs, normalize(path), false);
    }

    RoimPath(RoimFileSystem fs, char[] path, boolean navigationNormalized) {
        this.fs = fs;
        this.path = path;
        if (navigationNormalized)
            this.normalized = this;
    }

    // Converts to a character array, replaces any \'s with / and collapses any sequential /'s to a single /
    static char[] normalize(String data) {
        if (data.length() == 0)
            return new char[0];
        char[] chrs = data.toCharArray();
        int len = chrs.length;
        int prev = 0;
        for (int x = 0; x < len; x++) {
            char c = chrs[x];
            if (c == '\\')
                chrs[x] = c = '/';

            if (c == '/' && prev == '/') {
                int end = x;
                while (end++ < len && (chrs[end] == '/' || chrs[end] == '\\'));

                if (end < len) {
                    // There is more after the slash, shift it up.
                    int t = x;
                    for (int y = end; y < len; y++)
                        chrs[t++] = chrs[y];
                    len -= (end - x);
                    x--; //Back track one as we overwrote this character
                } else {
                    // There isn't, so trim to the last character
                    len = x;
                }
            }

            prev = c;
        }

        if (len > 1 && chrs[len - 1] == '/')
            len--; // Remove tailing / to mimic ZipPath

        // We collapsed something, resize array
        if (chrs.length != len)
            chrs = Arrays.copyOf(chrs, len);

        return chrs;
    }

    // Find all offsets for the start of each 'part', parts are split by / characters
    // If this path is empty then we have 1 part, of length 0
    private void initOffsets() {
        if (offsets != null)
            return;

        int count = 0;
        if (path.length == 0)
            count = 1;
        else {
            for (int x = 0; x < path.length; ) {
                char c = path[x++];
                if (c != '/') {
                    count++;
                    while (x < path.length && path[x++] != '/');
                }
            }
        }

        int[] result = new int[count];
        count = 0;
        for (int x = 0; x < path.length; x++) {
            char c = path[x];
            if (c != '/') {
                result[count++] = x;
                while (++x < path.length && path[x] != '/');
            }
        }

        synchronized (this) {
            if (this.offsets == null)
                this.offsets = result;
        }
    }

    private static RoimPath cast(Path path) {
        if (path == null)
            throw new NullPointerException();
        if (!(path instanceof RoimPath))
            throw new ProviderMismatchException();
        return (RoimPath)path;
    }

    @Override
    public int hashCode() {
        int ret = hashcode;
        if (ret == 0)
            ret = hashcode = Arrays.hashCode(path);
        return ret;
    }

    @Override
    public boolean equals(Object obj) {
        return obj instanceof RoimPath && this.fs == ((RoimPath)obj).fs && compareTo((Path)obj) == 0;
    }

    @Override
    public String toString() {
        return new String(path);
    }

    @Override
    public int compareTo(Path other) {
        RoimPath o = cast(other);
        int len = path.length;
        if (o.path.length < len)
            len = o.path.length;

        for (int x = 0; x < len; x++) {
            if (path[x] != o.path[x])
                return path[x] - o.path[x];
        }
        return path.length - o.path.length;
    }

    @Override
    public FileSystem getFileSystem() {
        return this.fs;
    }

    @Override
    public boolean isAbsolute() {
        return path.length > 0 && path[0] == '/';
    }

    @Override
    public Path getRoot() {
        return isAbsolute() ? this.fs.rootPath : null;
    }

    @Override
    public Path getFileName() {
        int x = path.length;
        if (x == 0) // ZipFileSystem returns null for this case, But DefaultFileSystem returns itself, I choose to follow DefaultFileSystem
            return this;
        if (x == 1 && path[0] == '/')
            return null;
        while (--x >= 0 && path[x] != '/');
        if (x < 0)
            return this;
        return new RoimPath(this.fs, Arrays.copyOfRange(path, x + 1, path.length), true);
    }

    @Override
    public Path getParent() {
        int x = path.length;
        if (x == 0 || (x == 1 && path[0] == '/'))
            return null;
        while (--x >= 0 && path[x] != '/');
        if (x <= 0)
            return getRoot();
        return new RoimPath(this.fs, Arrays.copyOfRange(path, 0, x), false);
    }

    @Override
    public int getNameCount() {
        initOffsets();
        return offsets.length;
    }

    @Override
    public Path getName(int index) {
        initOffsets();
        if (index < 0 || index >= offsets.length)
            throw new IllegalArgumentException();

        int start = offsets[index];
        int end;
        if (index == offsets.length - 1)
            end = path.length;
        else
            end = offsets[index + 1] - 1;

        return new RoimPath(this.fs, Arrays.copyOfRange(path, start, end), false);
    }

    @Override
    public Path subpath(int beginIndex, int endIndex) {
        initOffsets();
        if (beginIndex < 0 || beginIndex >= endIndex
            || beginIndex >= offsets.length
            || endIndex > offsets.length)
            throw new IllegalArgumentException();

        int start = offsets[beginIndex];
        int end;
        if (endIndex == offsets.length)
            end = path.length;
        else
            end = offsets[endIndex] - 1;

        return new RoimPath(this.fs, Arrays.copyOfRange(path, start, end), false);
    }

    @Override
    public boolean startsWith(String other) {
        return startsWith(fs.getPath(other));
    }

    @Override
    public boolean startsWith(Path other) {
        if (other == null)
            throw new NullPointerException();

        if (!(other instanceof RoimPath))
            return false;

        RoimPath o = (RoimPath)other;
        if (o.fs != this.fs
            || o.isAbsolute() != this.isAbsolute()
            || o.path.length > this.path.length)
            return false;

        // Check our starts match
        for (int x = 0; x < o.path.length; x++) {
            if (o.path[x] != this.path[x])
                return false;
        }

        // We're exactly the same
        if (o.path.length == this.path.length)
            return true;

        // If they are a directory (we matched the ending /)
        if (o.path[o.path.length - 1] == '/')
            return true;

        // They arn't explicitly a directory, but it matches ours
        return this.path[o.path.length] == '/';
    }

    @Override
    public boolean endsWith(String other) {
        return endsWith(fs.getPath(other));
    }

    @Override
    public boolean endsWith(Path other) {
        if (other == null)
            throw new NullPointerException();

        if (!(other instanceof RoimPath))
            return false;

        RoimPath o = (RoimPath)other;
        if (o.fs != this.fs)
            return false;

        // Normalize directory suffix
        int olen = o.path.length - 1;
        if (olen > 0 && o.path[olen] == '/')
            olen--;
        int tlen = path.length - 1;
        if (tlen > 0 && path[tlen] == '/')
            tlen--;

        // The other is empty
        if (olen == -1)
            return tlen == -1;

        // If its absolute, we have to be and match exact length after normalizing the directory ending
        if (o.isAbsolute()) {
            if (!this.isAbsolute() || olen != tlen)
                return false;
        }

        // If they are longer then us
        if (olen > tlen)
            return false;

        // Check if we match, walking backwards
        while (olen >= 0) {
            if (o.path[olen--] != path[tlen--])
                return false;
        }

        // If we've gotten here, We matched everything, so if the other is absolute it means we are to.
        if (o.isAbsolute())
            return true;

        // If we've reached the beginning of our path, or ended up at a directory, we're golden
        if (tlen == -1 || path[tlen] == '/')
            return true;

        return false;
    }

    @Override
    public Path normalize() {
        if (normalized == null)
            normalized = normalizeInternal();
        return this.normalized;
    }

    private Path normalizeInternal() {
        char[] data = null;
        int lastSep = -1;
        int write = 0;
        int len = path.length;

        for (int x = 0; x < len; x++) {
            char c = path[x];
            if (c == '/') {
                if (x <= 2) {
                    // 0 = "/foo", nothing to backtrack
                    // 2 = "../foo" which can't be backtracked
                    if (x == 1 && path[0] == '.') { // "./foo" -> "foo"
                        data = new char[len - 2];
                        continue;
                    }
                } else if (path[x - 1] == '.') {
                    if (lastSep == x - 2) { // "/./" -> "/"
                        if (data == null) {
                            data = new char[len - 2];
                            System.arraycopy(path, 0, data, 0, x - 1);
                            write = x - 1;
                            lastSep = x;
                            continue;
                        } else {
                            write -= 2;
                        }
                    } else if (path[x - 2] == '.' && lastSep == x - 3) { // "a/../b" -> "b"
                        if (data == null) {
                            write = x - 3; // remove ../
                            // Find the parent separator
                            while (write-- > 0 && path[write] != '/');

                            if (write <= 0) { // We've backtracked all the way to the beginning
                                data = new char[path.length - x];
                            } else {
                                data = new char[path.length - (x - write)];
                                System.arraycopy(path, 0, data, 0, write);
                            }

                        } else {
                            write -= 3; // remove ../
                            // Find the parent separator
                            while (write-- > 0 && data[write] != '/');
                        }

                        // can happen when the backtrack goes all the way to the root
                        if (write < 0) {
                            write = 0;
                            // We need to keep the absolute path to mimic ZipFileSystem
                            // /bad/../path -> /path
                            if (path[0] != '/')
                                continue;
                        }
                    }
                }
                lastSep = x;
            }

            if (data != null)
                data[write++] = c;
        }

        if (lastSep == len - 2 && path[len - 1] == '.') { // "something/." -> "something"
            if (data == null)
                return new RoimPath(fs, Arrays.copyOf(path, lastSep), true);
            write -= 2;
        } else if (lastSep == len - 3 && path[len - 1] == '.' && path[len - 2] == '.') { // "some/path/.." -> "some"
            if (data == null)
                return new RoimPath(fs, Arrays.copyOf(path, lastSep), true);
            else {
                write -= 3;
                while (write-- > 0 && data[write] != '/');
            }
        }

        if (data == null) // No fixes needed
            return this;

        if (data.length == write)
            return new RoimPath(fs, data, true);

        return new RoimPath(fs, Arrays.copyOfRange(data, 0, write), true);
    }

    @Override
    public Path resolve(String other) {
        char[] opath = normalize(other);
        if (opath.length == 0)
            return this;
        if (opath[0] == '/' || this.path.length == 0)
            return new RoimPath(fs, opath, false);
        return resolve(opath);
    }

    @Override
    public Path resolve(Path other) {
        RoimPath o = cast(other);
        if (o.path.length == 0)
            return this;
        if (o.isAbsolute() || this.path.length == 0)
            return o;
        return resolve(o.path);
    }

    private Path resolve(char[] opath) {
        char[] joined;
        if (path[path.length - 1] == '/') {
            joined = Arrays.copyOf(path, path.length + opath.length);
            System.arraycopy(opath, 0, joined, path.length, opath.length);
        } else {
            joined = Arrays.copyOf(path, path.length + 1 + opath.length);
            joined[path.length] = '/';
            System.arraycopy(opath, 0, joined, path.length + 1, opath.length);
        }
        return new RoimPath(fs, joined, false);
    }

    @Override
    public Path relativize(Path other) {
        RoimPath o = cast(other);

        if (this.equals(o))
            return new RoimPath(this.fs, new char[0], true);

        if (this.path.length == 0)
            return o;

        if (this.fs != o.fs)
            throw new IllegalArgumentException("Can't relativize across file systems");

        if (this.isAbsolute() != o.isAbsolute())
            throw new IllegalArgumentException("Can't relativize between absolute and non-absolute paths");

        if (this.path.length == 1 && this.path[0] == '/') // We are the root, so make the other non-absolute and return it.
            return new RoimPath(this.fs, Arrays.copyOfRange(o.path, 1, o.path.length), false);


        this.initOffsets();
        o.initOffsets();

        int len = offsets.length;
        if (o.offsets.length < len)
            len = o.offsets.length;

        // Find how many parts match
        int matched = 0;
        for (; matched < len; matched++) {
            int start = offsets[matched];
            if (start != o.offsets[matched])
                break;

            int end = matched == offsets.length - 1 ? path.length : offsets[matched + 1] - 1;
            int oend = matched == o.offsets.length - 1 ? o.path.length : o.offsets[matched + 1] - 1;

            if (end != oend)
                break;

            if (!matches(path, o.path, start, end))
                break;
        }

        int extra = getNameCount() - matched;
        int size = extra * 3 - 1; // Space for needed "../"'s without the slash at the end of the last one
        if (matched < o.getNameCount())
            size += o.path.length - o.offsets[matched] + 1; // Space for the rest of the other path, and a slash
        char[] ret = new char[size];

        int write = 0;
        for (int x = 0; x < extra; x++) {
            ret[write++] = '.';
            ret[write++] = '.';
            if (write != ret.length)
                ret[write++] = '/';
        }

        if (matched < o.getNameCount())
            System.arraycopy(o.path, o.offsets[matched], ret, write, o.path.length - o.offsets[matched]);

        return new RoimPath(this.fs, ret, false);
    }

    private static final boolean matches(char[] a, char[] b, int start, int end) {
        for (int x = start; x < end; x++) {
            if (a[x] != b[x])
                return false;
        }
        return true;
    }

    @Override
    public URI toUri() {
        try {
            RoimPath resolved = (RoimPath)(isAbsolute() ? normalize() : toAbsolutePath().normalize());
            return new URI(RoimFileSystemProvider.SCHEMA, fs.getKey() + new String(resolved.path), null);
        } catch (URISyntaxException e) {
            // It doesn't say in the javadocs, but both ZipFileSystem and WindowsFileSystem throw AssertionError when this happens
            throw new AssertionError(e);
        }
    }

    @Override
    public Path toAbsolutePath() {
        if (isAbsolute())
            return this;
        // We have no idea how this is relative to the root, so assume it is directly under the root
        char[] ret = new char[path.length + 1];
        System.arraycopy(path, 0, ret, 1, path.length);
        ret[0] = '/';
        return new RoimPath(this.fs, ret, false);
    }

    @Override
    public Path toRealPath(LinkOption... options) throws IOException {
        RoimPath resolved = getResolvedPath();
        this.fs.checkExists(resolved.toString());
        return resolved;
    }

    private RoimPath getResolvedPath() {
        if (resolved == null)
            resolved = (RoimPath)(isAbsolute() ? normalize() : toAbsolutePath().normalize());
        return resolved;
    }

    @Override
    public Path resolveSibling(String other) {
        return resolveSibling(fs.getPath(other));
    }

    @Override
    public Path resolveSibling(Path other) {
        Path parent = getParent();
        return parent == null ? other : parent.resolve(other);

    }

    @Override
    public Iterator<Path> iterator() {
        return new Iterator<Path>() {
            private int index = 0;

            @Override
            public boolean hasNext() {
                return index < getNameCount();
            }

            @Override
            public Path next() {
                if (index >= getNameCount())
                    throw new NoSuchElementException();
                return getName(index++);
            }

            @Override
            public void remove() {
                throw new ReadOnlyFileSystemException();
            }
        };
    }

    @Override
    public File toFile() {
        throw new UnsupportedOperationException();
    }

    @Override
    public WatchKey register(WatchService watcher, Kind<?>... events) throws IOException {
        return register(watcher, events, new WatchEvent.Modifier[0]);
    }

    @Override
    public WatchKey register(WatchService watcher, Kind<?>[] events, Modifier... modifiers) throws IOException {
        if (watcher == null || events == null || modifiers == null)
            throw new NullPointerException();
        // We don't support watchers, there will never be any change notifications.
        throw new ProviderMismatchException();
    }
}
