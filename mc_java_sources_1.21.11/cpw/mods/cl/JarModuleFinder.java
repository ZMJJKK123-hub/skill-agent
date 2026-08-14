/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package cpw.mods.cl;

import cpw.mods.jarhandling.SecureJar;
import net.minecraftforge.securemodules.SecureModuleFinder;

/** Moved to {@link SecureModuleFinder} */
@Deprecated(forRemoval = true)
public class JarModuleFinder extends SecureModuleFinder {
    private JarModuleFinder(final SecureJar... jars) {
        super(jars);
    }

    public static JarModuleFinder of(SecureJar... jars) {
        return new JarModuleFinder(jars);
    }
}
