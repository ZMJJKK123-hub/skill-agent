/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package cpw.mods.jarhandling;

import cpw.mods.jarhandling.impl.Jar;

import java.io.InputStream;
import java.lang.module.ModuleDescriptor;
import java.net.URI;
import java.nio.file.Path;
import java.security.CodeSigner;
import java.util.List;
import java.util.Optional;
import java.util.Set;
import java.util.function.BiPredicate;
import java.util.function.Function;
import java.util.function.Supplier;
import java.util.jar.Attributes;
import java.util.jar.Manifest;

public interface SecureJar {
    interface ModuleDataProvider {
        String name();
        ModuleDescriptor descriptor();
        URI uri();
        Optional<URI> findFile(String name);
        Optional<InputStream> open(final String name);

        Manifest getManifest();

        CodeSigner[] verifyAndGetSigners(String cname, byte[] bytes);
    }

    ModuleDataProvider moduleDataProvider();

    Path getPrimaryPath();

    CodeSigner[] getManifestSigners();

    Status verifyPath(Path path);

    Status getFileStatus(String name);

    Attributes getTrustedManifestEntries(String name);

    boolean hasSecurityData();

    static SecureJar from(final Path... paths) {
        return from(jar -> JarMetadata.from(jar, paths), paths);
    }

    static SecureJar from(BiPredicate<String, String> filter, final Path... paths) {
        return from(jar->JarMetadata.from(jar, paths), filter, paths);
    }

    static SecureJar from(Function<SecureJar, JarMetadata> metadataSupplier, final Path... paths) {
        return from(metadataSupplier, null, paths);
    }

    static SecureJar from(Function<SecureJar, JarMetadata> metadataSupplier, BiPredicate<String, String> filter, final Path... paths) {
        return new Jar(metadataSupplier, filter, paths);
    }

    /** Supplying a manifest is stupid. */
    @Deprecated(forRemoval = true, since = "2.2")
    static SecureJar from(Supplier<Manifest> defaultManifest, Function<SecureJar, JarMetadata> metadataSupplier, final Path... paths) {
        return from(defaultManifest, metadataSupplier, null, paths);
    }

    /** Supplying a manifest is stupid. */
    @Deprecated(forRemoval = true, since = "2.2")
    static SecureJar from(Supplier<Manifest> defaultManifest, Function<SecureJar, JarMetadata> metadataSupplier, BiPredicate<String, String> filter, final Path... paths) {
        return new Jar(defaultManifest, metadataSupplier, filter, paths);
    }

    Set<String> getPackages();

    List<Provider> getProviders();

    String name();

    Path getPath(String first, String... rest);

    Path getRootPath();

    // TODO: [SM] Make this record into an interface for API
    record Provider(String serviceName, List<String> providers) {
        @Deprecated
        public static Provider fromPath(Path path, BiPredicate<String, String> filter) {
            return Jar.getProvider(path, filter);
        }
    }

    enum Status {
        NONE, INVALID, UNVERIFIED, VERIFIED
    }
}
