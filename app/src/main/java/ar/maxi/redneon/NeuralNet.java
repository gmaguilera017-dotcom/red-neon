package ar.maxi.redneon;

import android.graphics.Bitmap;
import android.graphics.BlendMode;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.PorterDuff;
import android.graphics.PorterDuffXfermode;
import android.graphics.RadialGradient;
import android.graphics.RectF;
import android.graphics.Shader;
import android.os.Build;
import android.os.SystemClock;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;

/** Red neuronal de neón: racimos de colores + capas internas, con pulsos, destellos y tacto. */
final class NeuralNet {

    static final float[] HUES = {190, 150, 58, 28, 352, 318, 275, 228, 100, 12};
    static final int CAP = 1200;
    static final float AUTO_SPIN = 0.16f;

    float density = 1f;
    int W = 1, H = 1;
    float S = 1;

    // ---- nodos ----
    int n = 0;
    final float[] bx = new float[CAP], by = new float[CAP], bz = new float[CAP];
    final float[] hue = new float[CAP], k = new float[CAP], e = new float[CAP];
    final float[] am = new float[CAP], fx = new float[CAP], fy = new float[CAP], fz = new float[CAP];
    final float[] px = new float[CAP], py = new float[CAP], pz = new float[CAP];
    final float[] tw = new float[CAP], tp = new float[CAP];
    final float[] dx = new float[CAP], dy = new float[CAP], vx = new float[CAP], vy = new float[CAP];
    final int[] grp = new int[CAP], wave = new int[CAP], tf = new int[CAP];
    final boolean[] sat = new boolean[CAP];
    int[][] adj;

    // proyección
    final float[] sx = new float[CAP], sy = new float[CAP], st = new float[CAP], sper = new float[CAP];
    final float[] tr = new float[CAP * 12];
    int trI = 0;

    // ---- conexiones ----
    int ne;
    int[] ea, eb;
    int[] hubs;
    int core;

    // ---- estado ----
    double now = 0;
    float yaw = 0, pageYaw = 0, targetPageYaw = 0, pitch = 0.3f, shift = 0;
    double nextAmbient = 0.6;
    int waveId = 0;

    static final class Pend { int i; double at; float s; int w; }
    static final class Pulse { int a, b; float t, d, h; }
    static final class Ring { float x, y, t; }
    final ArrayList<Pend> pending = new ArrayList<>();
    final ArrayList<Pulse> pulses = new ArrayList<>();
    final ArrayList<Ring> rings = new ArrayList<>();

    // tacto
    boolean touching = false;
    float tx, ty, moved;
    long tDown, lastTapMs;

    // dibujo
    final Bitmap[] spriteN = new Bitmap[60], spriteS = new Bitmap[60];
    final Paint spritePaint = new Paint(Paint.FILTER_BITMAP_FLAG | Paint.ANTI_ALIAS_FLAG);
    final Paint linePaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    final Paint ringPaint = new Paint(Paint.ANTI_ALIAS_FLAG);
    final RectF rect = new RectF();

    private long seed = 11;

    NeuralNet() {
        build();
        for (Paint p : new Paint[]{spritePaint, linePaint, ringPaint}) {
            if (Build.VERSION.SDK_INT >= 29) p.setBlendMode(BlendMode.PLUS);
            else p.setXfermode(new PorterDuffXfermode(PorterDuff.Mode.ADD));
        }
        linePaint.setStyle(Paint.Style.STROKE);
        linePaint.setStrokeCap(Paint.Cap.ROUND);
        ringPaint.setStyle(Paint.Style.STROKE);
    }

    // ================= construcción =================

    private float rnd() { seed = (seed * 16807L) % 2147483647L; return (seed - 1) / 2147483646f; }
    private float gauss() { return (rnd() + rnd() + rnd() - 1.5f) / 0.75f; }

    private int add(float X, float Y, float Z, float h, int c, float kk) {
        int i = n++;
        bx[i] = X; by[i] = Y; bz[i] = Z; hue[i] = h; grp[i] = c; k[i] = kk; wave[i] = -1;
        return i;
    }

    private final ArrayList<int[]> E = new ArrayList<>();
    private final HashSet<Long> seen = new HashSet<>();

    private void link(int a, int b) {
        if (a == b) return;
        long key = a < b ? (((long) a) << 20) | b : (((long) b) << 20) | a;
        if (!seen.add(key)) return;
        E.add(new int[]{a, b});
    }

    private float d2(int a, int b) {
        float ddx = bx[a] - bx[b], ddy = by[a] - by[b], ddz = bz[a] - bz[b];
        return ddx * ddx + ddy * ddy + ddz * ddz;
    }

    private int[] nearest(final int a, int[] list, int cnt) {
        ArrayList<Integer> l = new ArrayList<>();
        for (int v : list) if (v != a) l.add(v);
        Collections.sort(l, (u, v) -> Float.compare(d2(a, u), d2(a, v)));
        int m = Math.min(cnt, l.size());
        int[] r = new int[m];
        for (int i = 0; i < m; i++) r[i] = l.get(i);
        return r;
    }

    private void build() {
        float GA = (float) (Math.PI * (3 - Math.sqrt(5)));
        core = add(0, 0, 0, 45, -1, 2.6f);
        int G = HUES.length;
        hubs = new int[G];
        int[][] groups = new int[G][];
        for (int ci = 0; ci < G; ci++) {
            float h = HUES[ci];
            float yy = 1 - 2 * (ci + .5f) / G;
            float rr = (float) Math.sqrt(1 - yy * yy);
            float th = GA * ci + .4f;
            float R = .82f + rnd() * .2f;
            float cx = (float) Math.cos(th) * rr * R * 1.08f, cy = yy * R * .98f, cz = (float) Math.sin(th) * rr * R;
            int hub = add(cx, cy, cz, h, ci, 2.1f);
            hubs[ci] = hub;
            float ax = .6f + rnd() * .9f, ay = .6f + rnd() * .9f, az = .6f + rnd() * .9f, sg = .17f + rnd() * .08f;
            int cnt = 14 + (int) (rnd() * 12);
            int[] list = new int[cnt + 1];
            list[0] = hub;
            for (int i = 1; i <= cnt; i++)
                list[i] = add(cx + gauss() * sg * ax, cy + gauss() * sg * ay, cz + gauss() * sg * az,
                        h + (rnd() - .5f) * 26, ci, .8f + rnd() * .5f);
            groups[ci] = list;
        }
        for (int[] list : groups) {
            int hub = list[0];
            for (int i = 1; i < list.length; i++) {
                int a = list[i];
                for (int b : nearest(a, list, 2)) link(a, b);
                if (rnd() < .4f) link(a, hub);
            }
            for (int b : nearest(hub, list, 4)) link(hub, b);
            link(core, hub);
        }
        for (int h : hubs) for (int o : nearest(h, hubs, 2)) link(h, o);
        for (int gi = 0; gi < G; gi++) {
            int[] list = groups[gi];
            for (int t = 0; t < 6; t++) {
                int a = list[1 + (int) (rnd() * (list.length - 1))];
                int best = -1;
                float bd = .6f;
                for (int j = 0; j < n; j++) {
                    if (grp[j] == gi || grp[j] < 0) continue;
                    float d = (float) Math.sqrt(d2(a, j));
                    if (d < bd) { bd = d; best = j; }
                }
                if (best >= 0) link(a, best);
            }
        }
        // capas internas
        float[][] shells = {{.34f, 14}, {.62f, 30}, {.9f, 52}};
        int[] prev = {core};
        for (int li = 0; li < shells.length; li++) {
            float r = shells[li][0];
            int cntS = (int) shells[li][1];
            float off = rnd() * 6.28f;
            int[] idx = new int[cntS];
            for (int i = 0; i < cntS; i++) {
                float yv = 1 - 2 * (i + .5f) / cntS, rr = (float) Math.sqrt(1 - yv * yv), th = GA * i + off;
                float X = (float) Math.cos(th) * rr * r * 1.05f, Z = (float) Math.sin(th) * rr * r, Y = yv * r * .97f;
                float bh = 0, bd = 1e9f;
                for (int hb : hubs) {
                    float ddx = bx[hb] - X, ddy = by[hb] - Y, ddz = bz[hb] - Z, d = ddx * ddx + ddy * ddy + ddz * ddz;
                    if (d < bd) { bd = d; bh = hue[hb]; }
                }
                idx[i] = add(X, Y, Z, bh + (rnd() - .5f) * 20, -2, .85f + rnd() * .3f);
            }
            for (int a : idx) for (int b : nearest(a, prev, li > 0 ? 2 : 3)) link(a, b);
            prev = idx;
        }
        for (int a : prev) for (int b : nearest(a, hubs, 1)) link(a, b);
        // satélites sueltos
        int base0 = n;
        int[] pool = new int[base0];
        for (int u = 0; u < base0; u++) pool[u] = u;
        for (int s = 0; s < 60; s++) {
            int gi = (int) (rnd() * G);
            int hb = hubs[gi];
            int si = add(bx[hb] + gauss() * .34f, by[hb] + gauss() * .3f, bz[hb] + gauss() * .34f,
                    HUES[gi] + (rnd() - .5f) * 30, gi, .55f + rnd() * .25f);
            sat[si] = true;
            for (int b : nearest(si, pool, 2)) link(si, b);
        }
        // poda: menos conexiones, nodos sueltos
        ArrayList<int[]> keep = new ArrayList<>();
        for (int[] ed : E) {
            int a = ed[0], b = ed[1];
            boolean kp;
            if (k[a] > 1.5f || k[b] > 1.5f) kp = true;
            else if (sat[a] || sat[b]) kp = rnd() > .78f;
            else kp = rnd() > .52f;
            if (kp) keep.add(ed);
        }
        ne = keep.size();
        ea = new int[ne];
        eb = new int[ne];
        int[] deg = new int[n];
        for (int i = 0; i < ne; i++) {
            ea[i] = keep.get(i)[0];
            eb[i] = keep.get(i)[1];
            deg[ea[i]]++;
            deg[eb[i]]++;
        }
        adj = new int[n][];
        for (int i = 0; i < n; i++) adj[i] = new int[deg[i]];
        int[] fill = new int[n];
        for (int i = 0; i < ne; i++) {
            adj[ea[i]][fill[ea[i]]++] = eb[i];
            adj[eb[i]][fill[eb[i]]++] = ea[i];
        }
        for (int i = 0; i < n; i++) {
            am[i] = (k[i] > 1.5f ? .02f : .06f) + rnd() * .06f + (k[i] < .8f ? .04f : 0);
            fx[i] = .5f + rnd() * .9f; fy[i] = .45f + rnd() * .9f; fz[i] = .5f + rnd() * .9f;
            px[i] = rnd() * 6.28f; py[i] = rnd() * 6.28f; pz[i] = rnd() * 6.28f;
            tw[i] = .5f + rnd() * 2.2f; tp[i] = rnd() * 6.28f;
        }
        E.clear();
        seen.clear();
    }

    // ================= entrada =================

    void resize(int w, int h) { W = Math.max(1, w); H = Math.max(1, h); S = Math.min(W, H); }

    void setPageOffset(float xOffset) { targetPageYaw = (xOffset - .5f) * 2.4f; }

    void touch(int action, float x, float y, long tMs) {
        switch (action) {
            case 0: // DOWN
                touching = true; tx = x; ty = y; tDown = tMs; moved = 0; break;
            case 2: // MOVE
                if (touching) { moved += Math.abs(x - tx) + Math.abs(y - ty); tx = x; ty = y; }
                break;
            case 1: // UP
                if (touching && moved < 10 * density && tMs - tDown < 350) tap(x, y);
                touching = false; break;
            case 3: // CANCEL
                touching = false; break;
            default: break;
        }
    }

    void tap(float x, float y) {
        long t = SystemClock.uptimeMillis();
        if (t - lastTapMs < 250) return;
        lastTapMs = t;
        Ring r = new Ring(); r.x = x; r.y = y; r.t = 0; rings.add(r);
        int best = -1;
        float bd = Float.MAX_VALUE, bonus = 400 * density * density;
        for (int i = 0; i < n; i++) {
            float ddx = sx[i] - x, ddy = sy[i] - y, d = ddx * ddx + ddy * ddy - st[i] * bonus;
            if (d < bd) { bd = d; best = i; }
        }
        if (best >= 0) fire(best, 1.05f);
    }

    private void fire(int i, float s) {
        waveId++;
        Pend p = new Pend(); p.i = i; p.at = now; p.s = s; p.w = waveId;
        pending.add(p);
    }

    // ================= simulación =================

    void step(float dt) {
        now += dt;
        yaw += AUTO_SPIN * dt;
        pageYaw += (targetPageYaw - pageYaw) * Math.min(1f, dt * 4f);
        pitch = .3f + .06f * (float) Math.sin(now * .13);
        if (now > nextAmbient) {
            int i = Math.random() < .35 ? hubs[(int) (Math.random() * hubs.length)] : (int) (Math.random() * n);
            fire(i, 1.15f);
            nextAmbient = now + .8 + Math.random() * 1.4;
        }
        shift = (float) ((now * 4) % 360);
        project();

        long ms = SystemClock.uptimeMillis();
        boolean hold = touching && moved < 14 * density && ms - tDown > 320;
        if (touching) {
            float R = S * .11f;
            for (int i = 0; i < n; i++) {
                float ddx = sx[i] - tx, ddy = sy[i] - ty, dd = ddx * ddx + ddy * ddy;
                if (dd < R * R && st[i] > .25f) {
                    float v = (1 - (float) Math.sqrt(dd) / R) * .75f;
                    if (v > e[i]) e[i] = v;
                }
            }
        }
        float RF = S * .22f, spring = (float) Math.exp(-dt * 3.2f);
        for (int i = 0; i < n; i++) {
            if (touching) {
                float ddx = sx[i] - tx, ddy = sy[i] - ty, dist = (float) Math.sqrt(ddx * ddx + ddy * ddy) + .001f;
                if (dist < RF) {
                    float fo = 1 - dist / RF, fs = (hold ? -1 : 1) * fo * fo * S * 2.2f * dt;
                    vx[i] += ddx / dist * fs;
                    vy[i] += ddy / dist * fs;
                }
            }
            vx[i] += -dx[i] * 9 * dt;
            vy[i] += -dy[i] * 9 * dt;
            vx[i] *= spring;
            vy[i] *= spring;
            dx[i] += vx[i] * dt;
            dy[i] += vy[i] * dt;
            sx[i] += dx[i];
            sy[i] += dy[i];
        }
        process();

        trI = (trI + 1) % 6;
        float decay = (float) Math.exp(-dt * 1.35f);
        for (int i = 0; i < n; i++) {
            tr[i * 12 + trI * 2] = sx[i];
            tr[i * 12 + trI * 2 + 1] = sy[i];
            if (tf[i] < 7) tf[i]++;
            e[i] *= decay;
            if (e[i] < .004f) e[i] = 0;
        }
        for (int m = pulses.size() - 1; m >= 0; m--) {
            Pulse u = pulses.get(m);
            u.t += dt;
            if (u.t >= u.d) pulses.remove(m);
        }
        for (int q = rings.size() - 1; q >= 0; q--) {
            Ring g = rings.get(q);
            g.t += dt;
            if (g.t > 1.1f) rings.remove(q);
        }
    }

    private void project() {
        float yw = yaw + pageYaw;
        float cY = (float) Math.cos(yw), sY = (float) Math.sin(yw), cP = (float) Math.cos(pitch), sP = (float) Math.sin(pitch);
        float cam = 3.8f, base = S * .33f * (W > H ? 1f : 1.1f);
        float br = 1 + .05f * (float) Math.sin(now * .45) + .02f * (float) Math.sin(now * 1.1);
        for (int i = 0; i < n; i++) {
            float x = bx[i] + (float) Math.sin(now * fx[i] + px[i]) * am[i];
            float y = by[i] + (float) Math.sin(now * fy[i] + py[i]) * am[i];
            float z = bz[i] + (float) Math.sin(now * fz[i] + pz[i]) * am[i];
            x *= br; y *= br; z *= br;
            float X = x * cY + z * sY, Z = -x * sY + z * cY;
            float y2 = y * cP - Z * sP, z2 = y * sP + Z * cP;
            float per = cam / (cam - z2), s = per * base;
            sx[i] = W / 2f + X * s;
            sy[i] = H / 2f + y2 * s;
            st[i] = (z2 + 1) / 2f;
            sper[i] = per;
        }
    }

    private void process() {
        for (int q = pending.size() - 1; q >= 0; q--) {
            if (q >= pending.size()) continue;
            Pend p = pending.get(q);
            if (p.at > now) continue;
            pending.remove(q);
            int i = p.i;
            if (wave[i] == p.w) continue;
            wave[i] = p.w;
            e[i] = Math.max(e[i], Math.min(1f, p.s));
            if (p.s < .18f || pulses.size() > 700) continue;
            for (int o : adj[i]) {
                if (wave[o] == p.w) continue;
                Pulse u = new Pulse(); u.a = i; u.b = o; u.t = 0; u.d = .16f; u.h = hue[i];
                pulses.add(u);
                Pend np = new Pend(); np.i = o; np.at = now + .16; np.s = p.s * .8f; np.w = p.w;
                pending.add(np);
            }
        }
    }

    // ================= dibujo =================

    void draw(Canvas c) {
        c.drawColor(0xFF03030A, PorterDuff.Mode.SRC);
        float d = density, sc = S / 700f;

        // nebulosas de color
        for (int h = 0; h < hubs.length; h++) {
            int i = hubs[h];
            float gs = S * .62f * sper[i] * (1 + .05f * (float) Math.sin(now * 1.1 + h));
            sprite(c, hue[i] + shift, true, sx[i], sy[i], gs, .045f + .03f * st[i]);
        }

        // conexiones
        for (int q = 0; q < ne; q++) {
            int a = ea[q], b = eb[q];
            float tz = (st[a] + st[b]) / 2, en = (e[a] + e[b]) / 2;
            float al = .02f + .11f * tz * tz + en * .5f;
            if (al < .02f) continue;
            linePaint.setColor(hsl(hue[a] + shift, 1f, (55 + en * 18) / 100f, Math.min(1f, al)));
            linePaint.setStrokeWidth((.5f + tz * .7f + en * 1.4f) * d);
            c.drawLine(sx[a], sy[a], sx[b], sy[b], linePaint);
        }

        // pulsos
        for (int m = 0; m < pulses.size(); m++) {
            Pulse u = pulses.get(m);
            float r = u.t / u.d;
            int a = u.a, b = u.b;
            float qx = sx[a] + (sx[b] - sx[a]) * r, qy = sy[a] + (sy[b] - sy[a]) * r, pt = st[a] + (st[b] - st[a]) * r;
            sprite(c, u.h + shift, false, qx, qy, (10 + 14 * pt) * sc, .3f + .3f * pt);
        }

        // estelas
        linePaint.setStrokeWidth(1.1f * d);
        int o = ((trI + 1) % 6) * 2;
        for (int i = 0; i < n; i++) {
            if (st[i] < .3f || (k[i] < .8f && st[i] < .5f) || tf[i] < 7) continue;
            float tx0 = tr[i * 12 + o], ty0 = tr[i * 12 + o + 1];
            float tl = (Math.abs(sx[i] - tx0) + Math.abs(sy[i] - ty0)) / d;
            if (tl < 2.5f) continue;
            linePaint.setColor(hsl(hue[i] + shift, 1f, .66f, Math.min(.3f, .04f + tl * .004f + e[i] * .15f)));
            c.drawLine(tx0, ty0, sx[i], sy[i], linePaint);
        }

        // nodos: lejos más chicos, tenues y borrosos; destellos a destiempo
        for (int i = 0; i < n; i++) {
            float t = st[i];
            boolean far = t < .42f;
            float twv = (float) Math.pow(.5 + .5 * Math.sin(now * tw[i] + tp[i]), 2.5);
            float size = (5 + 13 * t * t + e[i] * 40) * k[i] * sc * sper[i] * (far ? 1.5f : 1f) * (.8f + .6f * twv);
            float alpha = Math.min(.85f, (.08f + .55f * t * t) * (.45f + 1.1f * twv) + e[i] * .7f);
            sprite(c, hue[i] + shift, far && e[i] < .2f, sx[i], sy[i], size, alpha);
        }

        // ondas del toque
        ringPaint.setStrokeWidth(2 * d);
        for (int q = 0; q < rings.size(); q++) {
            Ring g = rings.get(q);
            ringPaint.setColor(hsl(190, 1f, .7f, .55f * (1 - g.t / 1.1f)));
            c.drawCircle(g.x, g.y, g.t * S * .28f, ringPaint);
        }
    }

    private void sprite(Canvas c, float h, boolean soft, float x, float y, float size, float alpha) {
        if (alpha <= 0.003f || size < .5f) return;
        int idx = Math.round(h / 6f) % 60;
        if (idx < 0) idx += 60;
        Bitmap[] arr = soft ? spriteS : spriteN;
        Bitmap b = arr[idx];
        if (b == null) { b = makeSprite(idx * 6f, soft); arr[idx] = b; }
        rect.set(x - size / 2, y - size / 2, x + size / 2, y + size / 2);
        spritePaint.setAlpha((int) (Math.min(1f, alpha) * 255));
        c.drawBitmap(b, null, rect, spritePaint);
    }

    private static Bitmap makeSprite(float h, boolean soft) {
        Bitmap b = Bitmap.createBitmap(96, 96, Bitmap.Config.ARGB_8888);
        Canvas cc = new Canvas(b);
        int[] cols;
        float[] stops;
        if (soft) {
            cols = new int[]{hsl(h, 1f, .72f, .55f), hsl(h, 1f, .58f, .2f), hsl(h, 1f, .5f, 0f)};
            stops = new float[]{0f, .45f, 1f};
        } else {
            cols = new int[]{hsl(h, .9f, .66f, 1f), hsl(h, 1f, .6f, .9f), hsl(h, 1f, .55f, .24f), hsl(h, 1f, .5f, 0f)};
            stops = new float[]{0f, .12f, .38f, 1f};
        }
        Paint p = new Paint();
        p.setShader(new RadialGradient(48, 48, 48, cols, stops, Shader.TileMode.CLAMP));
        cc.drawRect(0, 0, 96, 96, p);
        return b;
    }

    static int hsl(float h, float s, float l, float a) {
        h = ((h % 360) + 360) % 360 / 360f;
        float q = l < .5f ? l * (1 + s) : l + s - l * s, p = 2 * l - q;
        int r = (int) (hue2rgb(p, q, h + 1 / 3f) * 255 + .5f);
        int g = (int) (hue2rgb(p, q, h) * 255 + .5f);
        int b = (int) (hue2rgb(p, q, h - 1 / 3f) * 255 + .5f);
        int al = (int) (Math.max(0f, Math.min(1f, a)) * 255 + .5f);
        return (al << 24) | (r << 16) | (g << 8) | b;
    }

    private static float hue2rgb(float p, float q, float t) {
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1 / 6f) return p + (q - p) * 6 * t;
        if (t < 1 / 2f) return q;
        if (t < 2 / 3f) return p + (q - p) * (2 / 3f - t) * 6;
        return p;
    }
}
