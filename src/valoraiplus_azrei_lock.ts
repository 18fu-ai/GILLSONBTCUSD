import type { Router as TRouter, Request, Response, NextFunction } from "express";
import express from "express";
import fs from "fs";
import path from "path";
import { createHash } from "crypto";

type Opts = {
  valoraiplus_module_id: string;
  valoraiplus_GILLBTC: string;
  namespace: string;
  phbiUrl: string | undefined;
  logDir?: string;
  beaconUrl?: string;
};

// Placeholder for a function that would post JSON data
async function postJSON(url: string, payload: any): Promise<number> {
    // In a real implementation, this would make an HTTP POST request.
    // For this simulation, we'll just return a success code.
    console.log(`Simulating POST to ${url} with payload:`, payload);
    return 200;
}


export function valoraiplus_createAzreiRouter(opts: Opts): TRouter {
  const router = express.Router();
  const logDir = opts.logDir || path.resolve(process.cwd(), "logs");
  fs.mkdirSync(logDir, { recursive: true });
  const logFile = path.join(logDir, "valoraiplus_azrei_lock.log");

  // Middleware to process and store context
  router.use("/valoraiplus/azrei-lock", async (req: Request, res: Response, next: NextFunction) => {
    const ip = (req.headers["x-forwarded-for"] || (req.socket && req.socket.remoteAddress) || "0.0.0.0").toString().split(",")[0].trim();
    const ts = new Date().toISOString();
    const watermark = "VALORAIPLUS® WATERMARK ♥ ancient.penality.codex";
    const beaconHash = "0x" + createHash("sha256").update(ip + ts + watermark).digest("hex");

    let notified = false;
    const phbiUrl = process.env.VALORAIPLUS_PHBI_URL || process.env.SARA_PHBI_URL || opts.beaconUrl || "";
    if (phbiUrl) {
      try {
        const status = await postJSON(phbiUrl, {
            kind: "valoraiplus_azrei_beacon",
            ip, ts, beaconHash, watermark
        });
        notified = status >= 200 && status < 300;
        if (!notified) {
            fs.appendFileSync(logFile, JSON.stringify({ phbi_error: status, ts }) + "\n");
        }
      } catch (e: any) {
        fs.appendFileSync(logFile, JSON.stringify({ phbi_exception: e.message, ts }) + "\n");
      }
    }
    (req as any).__valoraiplus_azrei = { ip, ts, beaconHash, watermark, notified };
    next();
  });

  router.get("/valoraiplus/azrei-lock", (req: Request, res: Response) => {
    const ctx = (req as any).__valoraiplus_azrei || {};
    const head = ctx.notified ? "FEDERAL AUTHORITIES NOTIFIED" : "SECURITY INCIDENT RECORDED";

    // Simple HTML response to display the lock status
    res.status(403).send(`
      <!DOCTYPE html>
      <html>
        <head>
          <title>VALORAIPLUS_AZREILOCK :: ${head}</title>
          <style>
            body { background: #000; color: #f00; font-family: monospace; text-align: center; padding-top: 20%; }
            h1 { font-size: 2em; text-shadow: 0 0 5px #f00; }
            p { font-size: 1.2em; }
          </style>
        </head>
        <body>
          <h1>| VALORAIPLUS_AZREILOCK :: ${head} |</h1>
          <p>Your connection has been flagged for review.</p>
          <p>Beacon Hash: ${ctx.beaconHash || 'N/A'}</p>
        </body>
      </html>
    `);
  });

  return router;
}
