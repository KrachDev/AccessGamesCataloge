/**
 * AccessGames Analytics Tracker
 * Embed on public pages only. Admin page is local and reads from Supabase.
 * Table: page_views
 */
(function () {
  const SUPABASE_URL = 'https://nwyuyxailqogjfzspxex.supabase.co';
  const SUPABASE_ANON_KEY = 'sb_publishable_sM6H2xuqWjm8bH3v08NDMA_CSFO_GOU';

  // Don't track admin or local
  if (
    window.location.hostname === 'localhost' ||
    window.location.hostname === '127.0.0.1' ||
    window.location.pathname.includes('admin')
  ) return;

  const startTime = Date.now();

  function getDevice() {
    const ua = navigator.userAgent;
    if (/Mobi|Android|iPhone|iPad/i.test(ua)) return 'mobile';
    if (/Tablet|iPad/i.test(ua)) return 'tablet';
    return 'desktop';
  }

  function getBrowser() {
    const ua = navigator.userAgent;
    if (ua.includes('Firefox')) return 'Firefox';
    if (ua.includes('Edg')) return 'Edge';
    if (ua.includes('OPR') || ua.includes('Opera')) return 'Opera';
    if (ua.includes('Chrome')) return 'Chrome';
    if (ua.includes('Safari')) return 'Safari';
    return 'Other';
  }

  function getOS() {
    const ua = navigator.userAgent;
    if (ua.includes('Win')) return 'Windows';
    if (ua.includes('Mac')) return 'macOS';
    if (ua.includes('Android')) return 'Android';
    if (ua.includes('iPhone') || ua.includes('iPad')) return 'iOS';
    if (ua.includes('Linux')) return 'Linux';
    return 'Other';
  }

  function getReferrerSource(ref) {
    if (!ref) return 'Direct';
    try {
      const url = new URL(ref);
      const host = url.hostname.replace('www.', '');
      if (host.includes('google')) return 'Google';
      if (host.includes('bing')) return 'Bing';
      if (host.includes('t.me') || host.includes('telegram')) return 'Telegram';
      if (host.includes('twitter') || host.includes('x.com')) return 'Twitter/X';
      if (host.includes('facebook') || host.includes('fb.com')) return 'Facebook';
      if (host.includes('instagram')) return 'Instagram';
      if (host.includes('tiktok')) return 'TikTok';
      if (host.includes('youtube')) return 'YouTube';
      if (host.includes('reddit')) return 'Reddit';
      if (host.includes('whatsapp')) return 'WhatsApp';
      if (host.includes('discord')) return 'Discord';
      return host || 'Other';
    } catch {
      return 'Other';
    }
  }

  async function getCountry() {
    try {
      const res = await fetch('https://ipapi.co/json/', { signal: AbortSignal.timeout(3000) });
      if (res.ok) {
        const data = await res.json();
        return { country: data.country_name || 'Unknown', country_code: data.country_code || 'XX' };
      }
    } catch { /* silent */ }
    return { country: 'Unknown', country_code: 'XX' };
  }

  async function sendPageView() {
    const geo = await getCountry();

    const payload = {
      page: window.location.pathname.replace(/^\//, '') || 'index',
      page_title: document.title,
      referrer: document.referrer || null,
      referrer_source: getReferrerSource(document.referrer),
      device: getDevice(),
      browser: getBrowser(),
      os: getOS(),
      screen_width: window.screen.width,
      language: navigator.language || 'unknown',
      country: geo.country,
      country_code: geo.country_code,
      session_id: getOrCreateSession(),
      visited_at: new Date().toISOString()
    };

    try {
      await fetch(`${SUPABASE_URL}/rest/v1/page_views`, {
        method: 'POST',
        headers: {
          'apikey': SUPABASE_ANON_KEY,
          'Authorization': `Bearer ${SUPABASE_ANON_KEY}`,
          'Content-Type': 'application/json',
          'Prefer': 'return=minimal'
        },
        body: JSON.stringify(payload)
      });
    } catch { /* silent */ }
  }

  function getOrCreateSession() {
    const key = 'ag_session';
    let sid = sessionStorage.getItem(key);
    if (!sid) {
      sid = Math.random().toString(36).slice(2) + Date.now().toString(36);
      sessionStorage.setItem(key, sid);
    }
    return sid;
  }

  // Send on load
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', sendPageView);
  } else {
    sendPageView();
  }

  // Track session duration on leave
  window.addEventListener('beforeunload', async () => {
    const duration = Math.round((Date.now() - startTime) / 1000);
    const sid = getOrCreateSession();
    try {
      navigator.sendBeacon(`${SUPABASE_URL}/rest/v1/rpc/update_session_duration`, JSON.stringify({
        p_session_id: sid,
        p_duration: duration
      }));
    } catch { /* silent */ }
  });
})();
