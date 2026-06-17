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
            "src/mrhttp/internals/module.c",
            "src/mrhttp/internals/utils.c",
            "src/mrhttp/internals/app.c",
            "src/mrhttp/internals/protocol.c",
            "src/mrhttp/internals/mrqprotocol.c",
            "src/mrhttp/internals/mrqclient.c",
            "src/mrhttp/internals/memcachedclient.c",
            "src/mrhttp/internals/memprotocol.c",
            "src/mrhttp/internals/mrcacheclient.c",
            "src/mrhttp/internals/mrcacheprotocol.c",
            "src/mrhttp/internals/parser.c",
            "src/mrhttp/internals/request.c",
            "src/mrhttp/internals/response.c",
            "src/mrhttp/internals/router.c",
            "src/mrhttp/internals/mrhttpparser.c",
            "src/mrhttp/internals/hash/city.c",
            "src/mrhttp/internals/hash/assoc.c",
            "src/mrhttp/utils/unpack.c",
        },
        .flags = &.{
            "-std=gnu99", "-msse4.2", "-mavx2", "-mbmi2",
            "-Wno-discarded-qualifiers", "-Wno-unused-variable", "-Wno-unused-function",
        },
    });

    mod.addIncludePath(b.path("src/mrhttp/internals"));
    mod.addIncludePath(b.path("src/mrhttp/utils"));
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
    const out_name = b.fmt("src/mrhttp/internals{s}", .{ext_suffix});
    const install = b.addInstallFile(lib.getEmittedBin(), out_name);
    b.default_step.dependOn(&install.step);
}
