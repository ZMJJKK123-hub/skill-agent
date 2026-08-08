/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */

package net.minecraftforge.securemodules;

import java.net.URLStreamHandler;
import java.net.URLStreamHandlerFactory;
import java.net.spi.URLStreamHandlerProvider;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.ServiceLoader;

/**
 * This is our own solution to {@link java.net.spi.URLStreamHandlerProvider URLStreamHandlerProvider}
 * only supporting the system class path for discovering services.
 *
 * This *should* be a package private class, but for now, it's public so {@link cpw.mods.cl.ModularURLHandler} can find it.
 * I will make private once I break compatibility.
 */
public class LayerAwareURLStreamHandlerFactory implements URLStreamHandlerFactory {
    protected Map<String, Optional<URLStreamHandler>> handlers;
    private List<URLStreamHandlerProvider> services;

    protected void findProviders(ModuleLayer layer) {
        if (layer == null) {
            handlers = null;
            services = null;
        } else {
            handlers = new HashMap<>();
            services = ServiceLoader.load(layer, URLStreamHandlerProvider.class).stream()
                .map(ServiceLoader.Provider::get)
                .toList();
        }
    }

    @Override
    public URLStreamHandler createURLStreamHandler(final String protocol) {
        if (handlers == null) return null;
        var cached = handlers.get(protocol);
        if (cached != null)
            return cached.orElse(null);

        for (var service : services) {
            var handler = service.createURLStreamHandler(protocol);
            if (handler != null) {
                handlers.put(protocol, Optional.of(handler));
                return handler;
            }
        }

        handlers.put(protocol, Optional.empty());
        return null;
    }

}
