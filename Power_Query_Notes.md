# Power Query ETL / ELT notes

The seven CSV files in `Data/` are reproducible source exports. The Power BI semantic model embeds compressed copies so the project is portable without Windows-specific paths.

Each table is imported via Power Query M:

```powerquery
let
    CompressedCSV = Binary.FromText("<base64-compressed CSV>", BinaryEncoding.Base64),
    Source = Csv.Document(Binary.Decompress(CompressedCSV, Compression.Deflate), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, { /* typed columns */ }, "en-US")
in
    Typed
```

Transformation steps: load CSV bytes → decompress → parse CSV → promote headers → set dates, whole numbers, currency-like numerics and text. This is a **portable sample snapshot**, not an automatic connection to a live retailer. To swap data, replace the partition query with CSV/database imports, retaining the column names and star-schema keys.

## Encoding compatibility fix

The `Compression.Deflate` method in Power Query expects **raw DEFLATE** data (`zlib.compressobj(wbits=-15)`), not the zlib-wrapped data produced by `zlib.compress`. All seven embedded table payloads have been re-encoded and verified by round-trip decompression against their exact CSV source bytes.
