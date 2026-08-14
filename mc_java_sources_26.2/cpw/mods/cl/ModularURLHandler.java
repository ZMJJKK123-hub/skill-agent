/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package cpw.mods.cl;

import java.io.IOException;
import java.io.InputStream;
import java.io.UncheckedIOException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLStreamHandler;
import java.util.Optional;
import java.util.ServiceLoader;
import java.util.function.Function;

import net.minecraftforge.securemodules.LayerAwareURLStreamHandlerFactory;

/**
 * This is our own fancy service provider solution to {@link java.net.spi.URLStreamHandlerProvider URLStreamHandlerProvider}
 * only supporting the system class path for discovering services. For some dumb reasons cpw built a whole
 * custom service for this instead of reusing the one provided by Java.
 *
 * I suspect that nobody actually fucking knows what this class is, and why it exists.
 * It shouldn't be public API. There is no need for it.
 */
@Deprecated(forRemoval = true)
public class ModularURLHandler extends LayerAwareURLStreamHandlerFactory {
    /** This is what consumers are expected to implement as a service */
    @Deprecated(forRemoval = true)
    public interface IURLProvider {
        String protocol();
        Function<URL, InputStream> inputStreamFunction();
    }

    public static final ModularURLHandler INSTANCE = new ModularURLHandler();

    public static void initFrom(ModuleLayer layer) {
        new IllegalStateException("Who actually calls this? Report this stack trace to Forge").printStackTrace();
        INSTANCE.findProviders(layer);
    }

    @Override
    public void findProviders(ModuleLayer layer) {
        super.findProviders(layer);
        if (layer != null) {
            ServiceLoader.load(layer, IURLProvider.class).stream()
                .map(ServiceLoader.Provider::get)
                .forEach(provider -> {
                    handlers.put(provider.protocol(), Optional.of(new URLStreamHandler() {
                        @Override
                        protected URLConnection openConnection(URL u) throws IOException {
                            return new URLConnection(u) {
                                @Override public void connect() throws IOException {}
                                @Override
                                public InputStream getInputStream() throws IOException {
                                    try {
                                        return provider.inputStreamFunction().apply(url);
                                    } catch (UncheckedIOException e) {
                                        throw e.getCause();
                                    }
                                }
                            };
                        }
                    }));
                });
        }
    }
}
