const std = @import("std");

pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const opt = b.standardOptimizeOption(.{});

    const python_inc = b.option([]const u8, "python-include",
        "Path to Python include dir")
        orelse "/home/grandpa/.local/share/uv/python/cpython-3.14.2-linux-x86_64-gnu/include/python3.14";
    const python_lib = b.option([]const u8, "python-lib",
        "Path to Python lib dir")
        orelse "/home/grandpa/.local/share/uv/python/cpython-3.14.2-linux-x86_64-gnu/lib";

    const mod = b.createModule(.{
        .target = target,
        .optimize = opt,
    });

    mod.addCSourceFiles(.{
        .files = &.{
            "src/proapi/internals/module.c",
            "src/proapi/internals/utils.c",
            "src/proapi/internals/app.c",
            "src/proapi/internals/protocol.c",
            "src/proapi/internals/mrqprotocol.c",
            "src/proapi/internals/mrqclient.c",
            "src/proapi/internals/memcachedclient.c",
            "src/proapi/internals/memprotocol.c",
            "src/proapi/internals/mrcacheclient.c",
            "src/proapi/internals/mrcacheprotocol.c",
            "src/proapi/internals/parser.c",
            "src/proapi/internals/request.c",
            "src/proapi/internals/response.c",
            "src/proapi/internals/router.c",
            "src/proapi/internals/proapiparser.c",
            "src/proapi/internals/hash/city.c",
            "src/proapi/internals/hash/assoc.c",
            "src/proapi/utils/unpack.c",
        },
        .flags = &.{
            "-std=gnu99", "-msse4.2", "-mavx2", "-mbmi2",
            "-Wno-discarded-qualifiers", "-Wno-unused-variable", "-Wno-unused-function",
        },
    });

    mod.addIncludePath(b.path("src/proapi/internals"));
    mod.addIncludePath(b.path("src/proapi/utils"));
    mod.addIncludePath(.{ .cwd_relative = python_inc });

    mod.addLibraryPath(.{ .cwd_relative = python_lib });
    mod.linkSystemLibrary("pthread", .{});
    mod.linkSystemLibrary("dl", .{});
    mod.linkSystemLibrary("util", .{});
    mod.linkSystemLibrary("m", .{});
    mod.linkSystemLibrary("python3.14", .{});

    const lib = b.addLibrary(.{
        .name = "internals",
        .linkage = .dynamic,
        .root_module = mod,
    });

    const ext_suffix = ".cpython-314-x86_64-linux-gnu.so";
    const out_name = b.fmt("src/proapi/internals{s}", .{ext_suffix});
    const install = b.addInstallFile(lib.getEmittedBin(), out_name);
    b.default_step.dependOn(&install.step);
}
