/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package cpw.mods.cl;

import java.net.URL;
import java.security.*;
import java.util.HashMap;
import java.util.Map;

/**
 * This is just a class for caching code source and protection domains.
 * Honestly, nobody should ever of been using this, and it's superfluous now
 * that our ClassLoader extends {@link java.security.SecureClassLoader}
 */
@Deprecated(forRemoval = true)
public class ProtectionDomainHelper {
    private static final Map<URL, CodeSource> csCache = new HashMap<>();
    public static CodeSource createCodeSource(final URL url, final CodeSigner[] signers) {
        synchronized (csCache) {
            return csCache.computeIfAbsent(url, u->new CodeSource(url, signers));
        }
    }

    private static final Map<CodeSource, ProtectionDomain> pdCache = new HashMap<>();
    public static ProtectionDomain createProtectionDomain(CodeSource codeSource, ClassLoader cl) {
        synchronized (pdCache) {
            return pdCache.computeIfAbsent(codeSource, cs->{
                Permissions perms = new Permissions();
                perms.add(new AllPermission());
                return new ProtectionDomain(codeSource, perms, cl, null);
            });
        }
    }
}
