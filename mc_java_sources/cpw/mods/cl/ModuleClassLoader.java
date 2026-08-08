/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package cpw.mods.cl;

import java.io.FileNotFoundException;
import java.io.IOException;
import java.lang.module.Configuration;
import java.lang.module.ModuleReader;
import java.lang.module.ModuleReference;
import java.util.List;
import java.util.function.BiFunction;

import net.minecraftforge.securemodules.SecureModuleClassLoader;

@Deprecated(forRemoval = true)
public class ModuleClassLoader extends SecureModuleClassLoader {
    static {
        ClassLoader.registerAsParallelCapable();
    }

    /* ======================================================================
     * 				API Ment for modders to consume
     * ======================================================================
     */
    public ModuleClassLoader(String name, Configuration config, List<ModuleLayer> parentLayers) {
        super(name, null, config, parentLayers, List.of(), true);
    }

    public ModuleClassLoader(String name, ClassLoader parent, Configuration config, List<ModuleLayer> parentLayers, List<ClassLoader> parentLoaders, boolean unifySigners) {
        super(name, parent, config, parentLayers, parentLoaders, unifySigners);
    }

    @Override
    protected byte[] getClassBytes(ModuleReader reader, ModuleReference ref, String name) throws IOException {
        return super.getClassBytes(reader, ref, name);
    }

    @Override
    protected byte[] maybeTransformClassBytes(byte[] bytes, String name, String context) {
        return super.maybeTransformClassBytes(bytes, name, context);
    }

    @Override
    protected byte[] getMaybeTransformedClassBytes(String name, String context) throws ClassNotFoundException {
        return super.getMaybeTransformedClassBytes(name, context);
    }

    /* ======================================================================
     * 				BACKWARD COMPATIBILITY CRAP
     * ======================================================================
     */

    /**
     * modlauncher uses this to set the bootstrap classloader instead of using the System bootstrap.
     * But defaults to using the System bootstrap until this is overwritten
     * Honestly thats a stupid design and should just use the normal parental delegation like every
     * other classloader implementation.
     *
     * TODO: [SM][Deprecation] Remove fallback classloader
     */
    @Deprecated(forRemoval = true)
    public void setFallbackClassLoader(final ClassLoader fallbackClassLoader) {
        this.fallbackClassLoader = fallbackClassLoader;
    }

    /**
     * Who consumes this? You should tell me on discord, why you use it instead of other standard ClassLoader functions
     */
    @Deprecated(forRemoval = true)
    protected <T> T loadFromModule(final String moduleName, BiFunction<ModuleReader, ModuleReference, T> lookup) throws IOException {
        var module = configuration.findModule(moduleName).orElseThrow(FileNotFoundException::new);
        var ref = module.reference();
        try (var reader = ref.open()) {
            return lookup.apply(reader, ref);
        }
    }

    /**
     * I honestly have no idea why this would be protected instead of private. If you use it let me know.
     */
    @Deprecated(forRemoval = true)
    protected String classNameToModuleName(String name) {
        return super.classNameToModuleName(name);
    }
}
