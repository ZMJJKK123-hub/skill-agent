/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

@SuppressWarnings("removal")
module cpw.mods.securejarhandler {
    // Backwards compatibility crap, delete when moving to our own module.
    exports cpw.mods.jarhandling;
    exports cpw.mods.jarhandling.impl; // TODO - Bump version, and remove this export, you don't need our implementation
    exports cpw.mods.cl;
    exports cpw.mods.niofs.union;

    exports net.minecraftforge.securemodules;

    requires org.objectweb.asm;
    requires org.objectweb.asm.tree;
    requires java.base;

    requires jdk.unsupported;
    requires net.minecraftforge.unsafe;

    // TODO: [SM] Move UnionFS out into its own project
    provides java.nio.file.spi.FileSystemProvider
        with cpw.mods.niofs.union.UnionFileSystemProvider;

    uses java.net.spi.URLStreamHandlerProvider;
    provides java.net.spi.URLStreamHandlerProvider with
        cpw.mods.niofs.union.UnionURLStreamHandlerProvider;

    uses cpw.mods.cl.ModularURLHandler.IURLProvider;
    provides cpw.mods.cl.ModularURLHandler.IURLProvider with
        cpw.mods.cl.UnionURLStreamHandler;
}