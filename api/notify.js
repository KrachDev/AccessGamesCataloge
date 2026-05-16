export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { text } = req.body;
  if (!text) {
    return res.status(400).json({ error: 'Missing text parameter' });
  }

  // Fetch from Environment Variables configured in Vercel
  const BOT_TOKEN = process.env.TG_BOT_TOKEN;
  const CHAT_ID = process.env.TG_CHAT_ID;

  if (!BOT_TOKEN || !CHAT_ID) {
    console.error('Server misconfiguration: Missing TG_BOT_TOKEN or TG_CHAT_ID');
    return res.status(500).json({ error: 'Server misconfiguration' });
  }

  try {
    const response = await fetch(`https://api.telegram.org/bot${BOT_TOKEN}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chat_id: CHAT_ID, text: text })
    });
    
    // We only return a simple success or fail to the client.
    // This prevents leaking any Telegram internal IDs (like message_id, bot info) back to the Network Tab.
    if (!response.ok) {
      console.error('Telegram API error:', await response.text());
      return res.status(500).json({ error: 'Failed to send message' });
    }
    
    return res.status(200).json({ success: true });
  } catch (e) {
    console.error('Notify error:', e);
    return res.status(500).json({ error: 'Internal server error' });
  }
}
