/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package cpw.mods.util;

import net.minecraftforge.unsafe.UnsafeHacks;

import java.lang.invoke.MethodHandle;
import java.lang.invoke.MethodHandles;
import java.lang.invoke.MethodType;
import java.nio.channels.FileChannel;
import java.nio.channels.SeekableByteChannel;
import java.nio.file.FileSystem;
import java.nio.file.Path;

/**
 * Hacky utilities to access interals of ZipFileSystem to prevent thread interrrupts for breaking the entire FileSystem for everyone else.
 * This is an internal class, not exposed in module-info. If you're using this as a consumer, Don't.
 * See: https://github.com/MinecraftForge/SecureModules/pull/8
 * The ZipPath.exists invocation is for a performance optimization.
 */
public class ZipUtils {
    private static final MethodHandle ZIPFS_EXISTS;
    private static final MethodHandle ZIPFS_CH;
    private static final MethodHandle FCI_UNINTERUPTIBLE;

    static {
        try {
            var hackfield = MethodHandles.Lookup.class.getDeclaredField("IMPL_LOOKUP");
            UnsafeHacks.setAccessible(hackfield);
            MethodHandles.Lookup hack = (MethodHandles.Lookup) hackfield.get(null);

            var clz = Class.forName("jdk.nio.zipfs.ZipPath");
            ZIPFS_EXISTS = hack.findSpecial(clz, "exists", MethodType.methodType(boolean.class), clz);

            clz = Class.forName("jdk.nio.zipfs.ZipFileSystem");
            ZIPFS_CH = hack.findGetter(clz, "ch", SeekableByteChannel.class);

            clz = Class.forName("sun.nio.ch.FileChannelImpl");
            FCI_UNINTERUPTIBLE = hack.findSpecial(clz, "setUninterruptible", MethodType.methodType(void.class), clz);
        } catch (NoSuchFieldException | IllegalAccessException | ClassNotFoundException | NoSuchMethodException e) {
            throw new RuntimeException(e);
        }
    }

    public static SeekableByteChannel getByteChannel(final FileSystem zfs) throws Throwable {
        return (SeekableByteChannel) ZIPFS_CH.invoke(zfs);
    }

    public static void setUninterruptible(final SeekableByteChannel byteChannel) throws Throwable {
        if (byteChannel instanceof FileChannel) {
            FCI_UNINTERUPTIBLE.invoke(byteChannel);
        }
    }

    public static void setUninterruptible(final FileSystem fileSystem) throws Throwable {
        try {
            SeekableByteChannel byteChannel = getByteChannel(fileSystem);
            setUninterruptible(byteChannel);
        } catch (ClassCastException e) {
            // ZipFileSystem is private, so we can't do a normal check, so just eat the exception
        }
    }

    public static boolean exists(final Path path) throws Throwable {
        return (boolean) ZIPFS_EXISTS.invoke(path);
    }
}
