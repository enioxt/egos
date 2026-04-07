/**
 * atrian-stream.ts — Real-time stream-side ATRiAN filter
 *
 * Creates a TransformStream<string, string> that redacts a blocklist of
 * critical entities from each text chunk as it streams to the client.
 *
 * Use alongside post-hoc validateAndLog (which runs on full completed text
 * and catches semantic violations like absolute claims and false promises).
 * This filter only handles the critical-entity blocking that must happen
 * in real-time — don't use it to replace full validation.
 *
 * Usage (Vercel AI SDK):
 *   const filter = createAtrianStreamTransform(['term1', 'term2']);
 *   return new Response(
 *     result.textStream.pipeThrough(filter).pipeThrough(new TextEncoderStream()),
 *     { headers: { 'Content-Type': 'text/plain; charset=utf-8', ...headers } }
 *   );
 *
 * Usage (Node.js / other):
 *   const filter = createAtrianStreamTransform(BLOCKED_ENTITIES);
 *   const filtered = readableStream.pipeThrough(filter);
 */

/**
 * Returns a passthrough TransformStream when blockedEntities is empty,
 * or a redacting transform that replaces matched terms with ***.
 */
export function createAtrianStreamTransform(
  blockedEntities: string[],
): TransformStream<string, string> {
  if (blockedEntities.length === 0) {
    // identity — no performance cost
    return new TransformStream<string, string>();
  }

  const regex = new RegExp(
    blockedEntities.map(e => e.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|'),
    'gi',
  );

  return new TransformStream<string, string>({
    transform(chunk, controller) {
      controller.enqueue(chunk.replace(regex, '***'));
    },
  });
}
