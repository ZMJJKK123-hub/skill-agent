/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.roimfs;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URL;
import java.net.URLConnection;
import java.net.URLStreamHandler;
import java.nio.charset.StandardCharsets;
import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Locale;

public class Handler extends URLStreamHandler {
    private static final String PROPERTY = "java.protocol.handler.pkgs";
    private static boolean registered = false;

    static void register() {
        if (registered)
            return;
        registered = true;

        String env = System.getProperty(PROPERTY);
        if (env == null)
            env = "net.minecraftforge";
        else
            env += "|net.minecraftforge";
        System.setProperty(PROPERTY, env);
    }


    @Override
    protected URLConnection openConnection(URL url) throws IOException {
        return new Connection(url);
    }

    private static class Connection extends URLConnection {
        private InputStream stream;
        private int size;

        protected Connection(URL url) {
            super(url);
        }

        @Override
        public void connect() throws IOException {
            if (stream != null)
                return;

            Path path = Paths.get(toUri(url));
            if (Files.isDirectory(path)) {
                // Java's 'file' url handler treats directories as a list of files with \n separation, so do the same
                StringBuilder sb = new StringBuilder();
                try (DirectoryStream<Path> files = Files.newDirectoryStream(path)) {
                    for (Path file : files)
                        sb.append(file.getFileName()).append('\n');
                }
                byte[] data = sb.toString().getBytes(StandardCharsets.UTF_8);
                stream = new ByteArrayInputStream(data);
                size = data.length;
            } else {
                stream = Files.newInputStream(path);
                size = (int)Files.size(path);
            }
        }

        @Override
        public InputStream getInputStream() throws IOException {
            connect();
            return stream;
        }

        @Override
        public String getHeaderField(String name) {
            try {
                connect();
            } catch (IOException e) {
                return null;
            }

            name = name.toLowerCase(Locale.ENGLISH);
            if ("content-length".equals(name))
                return Integer.toString(size);
            if ("content-type".equals(name))
                return "application/octet-stream";

            return null;
        }
    }

    private static URI toUri(URL url) throws IOException {
        try {
            return url.toURI();
        } catch (URISyntaxException e) {
            throw new IOException("URL " + url + " cannot be converted to a URI", e);
        }
    }
}
