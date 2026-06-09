// 下一顿吃什么 - Service Worker
// 实现离线可用 + "安装"到桌面

const CACHE_NAME = 'meal-picker-v5';
const FILES_TO_CACHE = [
  '.',
  'index.html',
  'manifest.json',
  'favicon.svg',
  'icon-192.png',
  'icon-512.png',
  'apple-touch-icon.png'
];

// 安装：预缓存核心文件
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(FILES_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// 激活：清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// 判断是否为页面请求（HTML）
function isPageRequest(request) {
  return request.mode === 'navigate' ||
    (request.method === 'GET' &&
     request.headers.get('accept') &&
     request.headers.get('accept').includes('text/html'));
}

// 请求拦截：HTML 网络优先（确保拿到最新版），其他资源缓存优先
self.addEventListener('fetch', (event) => {
  // 对 HTML 页面请求：网络优先，失败时回退缓存
  if (isPageRequest(event.request)) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // 网络成功 → 更新缓存并返回
          if (response && response.status === 200) {
            const clone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, clone);
            });
          }
          return response;
        })
        .catch(() => {
          // 网络失败（离线）→ 返回缓存
          return caches.match(event.request).then(
            (cached) => cached || caches.match('index.html')
          );
        })
    );
    return;
  }

  // 非 HTML 资源（CSS/JS/图标等）：缓存优先，网络回退
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request).then((response) => {
        if (response && response.status === 200) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, clone);
          });
        }
        return response;
      });
    }).catch(() => {
      return caches.match('index.html');
    })
  );
});
