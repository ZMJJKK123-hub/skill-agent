/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.accesstransformer.parser;


import java.util.Locale;

import net.minecraftforge.accesstransformer.AccessTransformer.FinalState;
import net.minecraftforge.accesstransformer.AccessTransformer.Modifier;

public final class ModifierProcessor {
    private ModifierProcessor() {}

    public static Modifier modifier(String modifierString) {
        String modifier = modifierString.toUpperCase(Locale.ROOT);

        char f = modifier.charAt(modifier.length() - 1);
        char op = modifier.charAt(modifier.length() - 2);

        if (f == 'F' && (op == '-' || op == '+'))
            modifier = modifier.substring(0, modifier.length() - 2);

        switch (modifier) {
            case "PUBLIC": return Modifier.PUBLIC;
            case "PROTECTED": return Modifier.PROTECTED;
            case "DEFAULT": return Modifier.DEFAULT;
            case "PRIVATE": return Modifier.PRIVATE;
            default: return null;
        }
    }

    public static FinalState finalState(String modifierString) {
        final String modifier = modifierString.toUpperCase(Locale.ROOT);

        char f = modifier.charAt(modifier.length() - 1);
        if (f != 'F')
            return FinalState.LEAVE;

        char op = modifier.charAt(modifier.length() - 2);
        if (op == '-')
            return FinalState.REMOVEFINAL;
        if (op == '+')
            return FinalState.MAKEFINAL;

        return FinalState.LEAVE;
    }
}
