package net.minecraft.server.permissions;

public interface PermissionSet {
    PermissionSet NO_PERMISSIONS = p_454721_ -> false;
    PermissionSet ALL_PERMISSIONS = p_454823_ -> true;

    boolean hasPermission(Permission p_453055_);

    default PermissionSet union(PermissionSet p_459238_) {
        return (PermissionSet)(p_459238_ instanceof PermissionSetUnion ? p_459238_.union(this) : new PermissionSetUnion(this, p_459238_));
    }
}
