/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package net.minecraftforge.securemodules;

import java.lang.module.ModuleDescriptor;
import java.lang.module.ModuleReference;
import java.net.URI;
import java.security.CodeSigner;
import java.util.jar.Attributes;

/**
 * A module reference that includes the extra information needed
 * for ModuleClassLoader to properly create packages and signatures
 */
public abstract class SecureModuleReference extends ModuleReference {
    protected SecureModuleReference(ModuleDescriptor descriptor, URI location) {
        super(descriptor, location);
    }

    /**
     * Gets the main attributes of the module, this is typically just the jar's main attributes
     */
    public abstract Attributes getMainAttributes();

    /**
     * Gets the attributes for a specific entry, typically a package.
     * Should only return trusted values. Either from an unsigned jar,
     * or one with verified manifest signatures.
     */
    public abstract Attributes getTrustedAttributes(String entry);

    /*
     * Returns the code signers that are verified to match the supplied entry and data.
     */
    public abstract CodeSigner[] getCodeSigners(String entry, byte[] data);
}
