// Placeholder for epic
export function normalizeCore(core: any) {
    return core;
}

export function stableCanonicalJson(obj: any) {
    return JSON.stringify(obj, Object.keys(obj).sort());
}
