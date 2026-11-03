package ar.maxi.redneon;

import android.app.WallpaperManager;
import android.graphics.Canvas;
import android.os.Build;
import android.os.Bundle;
import android.service.wallpaper.WallpaperService;
import android.view.Choreographer;
import android.view.MotionEvent;
import android.view.SurfaceHolder;

public class NeuralWallpaperService extends WallpaperService {

    @Override
    public Engine onCreateEngine() {
        return new NeuralEngine();
    }

    class NeuralEngine extends Engine implements Choreographer.FrameCallback {
        private final NeuralNet net = new NeuralNet();
        private boolean running = false;
        private long lastDrawNs = 0;

        @Override
        public void onCreate(SurfaceHolder holder) {
            super.onCreate(holder);
            setTouchEventsEnabled(true);
            net.density = getResources().getDisplayMetrics().density;
        }

        @Override
        public void onSurfaceChanged(SurfaceHolder holder, int format, int width, int height) {
            super.onSurfaceChanged(holder, format, width, height);
            net.resize(width, height);
            net.step(0.016f);
            drawFrame();
        }

        @Override
        public void onVisibilityChanged(boolean visible) {
            if (visible) start(); else stop();
        }

        @Override
        public void onSurfaceDestroyed(SurfaceHolder holder) {
            stop();
            super.onSurfaceDestroyed(holder);
        }

        @Override
        public void onDestroy() {
            stop();
            super.onDestroy();
        }

        @Override
        public void onOffsetsChanged(float xOffset, float yOffset, float xStep, float yStep, int xPixels, int yPixels) {
            net.setPageOffset(xOffset);
        }

        @Override
        public void onTouchEvent(MotionEvent event) {
            int a = event.getActionMasked();
            if (a == MotionEvent.ACTION_DOWN || a == MotionEvent.ACTION_MOVE
                    || a == MotionEvent.ACTION_UP || a == MotionEvent.ACTION_CANCEL) {
                net.touch(a, event.getX(), event.getY(), event.getEventTime());
            } else if (a == MotionEvent.ACTION_POINTER_DOWN) {
                net.touch(MotionEvent.ACTION_CANCEL, 0, 0, event.getEventTime());
            }
        }

        @Override
        public Bundle onCommand(String action, int x, int y, int z, Bundle extras, boolean resultRequested) {
            if (WallpaperManager.COMMAND_TAP.equals(action)) net.tap(x, y);
            return super.onCommand(action, x, y, z, extras, resultRequested);
        }

        private void start() {
            if (running) return;
            running = true;
            lastDrawNs = 0;
            Choreographer.getInstance().postFrameCallback(this);
        }

        private void stop() {
            running = false;
            Choreographer.getInstance().removeFrameCallback(this);
        }

        @Override
        public void doFrame(long frameTimeNanos) {
            if (!running) return;
            Choreographer.getInstance().postFrameCallback(this);
            // ~30 cuadros por segundo para cuidar la batería
            if (lastDrawNs != 0 && frameTimeNanos - lastDrawNs < 31_000_000L) return;
            float dt = lastDrawNs == 0 ? 0.033f : (frameTimeNanos - lastDrawNs) / 1e9f;
            lastDrawNs = frameTimeNanos;
            net.step(Math.min(dt, 0.05f));
            drawFrame();
        }

        private void drawFrame() {
            SurfaceHolder holder = getSurfaceHolder();
            Canvas c = null;
            try {
                if (Build.VERSION.SDK_INT >= 26) {
                    try {
                        c = holder.lockHardwareCanvas();
                    } catch (Exception ignored) {
                        c = null;
                    }
                }
                if (c == null) c = holder.lockCanvas();
                if (c != null) net.draw(c);
            } catch (Exception ignored) {
                // superficie no disponible: se reintenta en el próximo cuadro
            } finally {
                if (c != null) {
                    try {
                        holder.unlockCanvasAndPost(c);
                    } catch (Exception ignored) {
                    }
                }
            }
        }
    }
}
