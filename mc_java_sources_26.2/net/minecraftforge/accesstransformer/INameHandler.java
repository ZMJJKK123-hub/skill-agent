/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.accesstransformer;

public interface INameHandler {
    String translateClassName(String className);
    String translateFieldName(String fieldName);
    String translateMethodName(String methodName);
}
