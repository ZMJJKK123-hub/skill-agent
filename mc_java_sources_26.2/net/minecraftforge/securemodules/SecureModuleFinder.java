/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package net.minecraftforge.securemodules;

import cpw.mods.jarhandling.SecureJar;
import java.io.IOException;
import java.io.InputStream;
import java.lang.module.ModuleFinder;
import java.lang.module.ModuleReader;
import java.lang.module.ModuleReference;
import java.net.URI;
import java.security.CodeSigner;
import java.util.*;
import java.util.jar.Attributes;
import java.util.jar.Manifest;
import java.util.stream.Stream;

/**
 *
 */
public class SecureModuleFinder implements ModuleFinder {
    private final Map<String, ModuleReference> references = new HashMap<>();

    protected SecureModuleFinder(final Iterable<SecureJar> jars) {
        for (var jar : jars) {
            var data = jar.moduleDataProvider();
            if (references.containsKey(data.name()))
                System.out.println("Ignoring duplicate module on SecureModuleFinder: " + data.name() + ": " + jar);
            else
                references.put(data.name(), new Reference(data));
        }
    }

    protected SecureModuleFinder(final SecureJar... jars) {
        this(Arrays.asList(jars));
    }

    @Override
    public Optional<ModuleReference> find(final String name) {
        return Optional.ofNullable(references.get(name));
    }

    @Override
    public Set<ModuleReference> findAll() {
        return new HashSet<>(references.values());
    }

    public static SecureModuleFinder of(SecureJar... jars) {
        return new SecureModuleFinder(jars);
    }

    public static SecureModuleFinder of(Iterable<SecureJar> jars) {
        return new SecureModuleFinder(jars);
    }

    private static class Reference extends SecureModuleReference {
        private final SecureJar.ModuleDataProvider jar;
        private final Manifest manifest;

        Reference(final SecureJar.ModuleDataProvider jar) {
            super(jar.descriptor(), jar.uri());
            this.jar = jar;
            this.manifest = jar.getManifest();
        }

        @Override
        public ModuleReader open() throws IOException {
            return new Reader(this.jar);
        }

        @Override
        public Attributes getMainAttributes() {
            return manifest == null ? null : manifest.getMainAttributes();
        }

        @Override
        public Attributes getTrustedAttributes(String entry) {
            // TODO: [SM] Add API to Secure jar to get Trusted Attributes
            return manifest == null ? null : manifest.getAttributes(entry);
        }

        @Override
        public CodeSigner[] getCodeSigners(String entry, byte[] data) {
            return this.jar.verifyAndGetSigners(entry, data);
        }
    }

    private record Reader(SecureJar.ModuleDataProvider jar) implements ModuleReader {
        @Override
        public Optional<URI> find(final String name) throws IOException {
            return jar.findFile(name);
        }

        @Override
        public Optional<InputStream> open(final String name) throws IOException {
            return jar.open(name);
        }

        @Override
        public Stream<String> list() throws IOException {
            return null;
        }

        @Override
        public void close() throws IOException {
        }

        @Override
        public String toString() {
            return "JarModuleFinder.Reader[jar=" + jar + "]";
        }
    }
}
