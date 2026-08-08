/*
 * Copyright (c) Forge Development LLC
 * SPDX-License-Identifier: LGPL-2.1-only
 */
package net.minecraftforge.accesstransformer;

import java.util.Objects;
import java.util.Set;

import org.objectweb.asm.Opcodes;
import org.objectweb.asm.tree.MethodNode;

public class MethodTarget extends Target<MethodNode> {
    private final String targetName;

    public MethodTarget(String className, String methodName, String desc) {
        super(className);
        this.targetName = methodName + desc;
    }

    @Override
    public TargetType getType() {
        return TargetType.METHOD;
    }

    @Override
    public String toString() {
        return super.toString() + " " + this.targetName;
    }

    @Override
    public boolean equals(final Object obj) {
        if (!(obj instanceof MethodTarget)) return false;
        MethodTarget o = (MethodTarget)obj;
        return super.equals(obj) && Objects.equals(targetName, o.targetName);
    }

    @Override
    public int hashCode() {
        return Objects.hash(getClassName(), getType(), targetName);
    }

    @Override
    public String targetName() {
        return targetName;
    }

    @Override
    public void apply(final MethodNode node, final AccessTransformer.Modifier targetAccess, final AccessTransformer.FinalState targetFinalState, Set<String> privateChanged) {
        boolean wasPrivate = (node.access & Opcodes.ACC_PRIVATE) == Opcodes.ACC_PRIVATE;
        node.access = targetAccess.mergeWith(node.access);
        node.access = targetFinalState.mergeWith(node.access);
        if (wasPrivate && !"<init>".equals(node.name) && (node.access & Opcodes.ACC_PRIVATE) != Opcodes.ACC_PRIVATE)
            privateChanged.add(node.name+node.desc);
    }
}
