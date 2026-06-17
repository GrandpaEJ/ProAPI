# Serialization (mrpacker)

ProAPI includes mrpacker — a fast binary serialization format compiled directly into the C extension.

```python
import proapi

# Pack
data = proapi.pack({'hello': 'world', 'nums': [1, 2, 3]})
print(data.hex())
# 22 81 65 68 65 6c 6c 6f 85 77 6f 72 6c 64 84 6e 75 6d 73 c3 c1 c2 c3

# Unpack
obj = proapi.unpack(data)
print(obj)
# {'hello': 'world', 'nums': [1, 2, 3]}
```

## Supported types

None, bool, int (up to 64-bit), float, str, bytes, list, tuple, dict.

## Performance

Faster than JSON, more compact than msgpack. Zero external dependencies.
