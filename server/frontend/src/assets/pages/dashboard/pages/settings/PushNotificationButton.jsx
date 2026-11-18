import { useState, useEffect } from 'react';
import api from '../../../../../api/axios';
import Toggle from '../../../../ui/toogles/toggles';

const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY;

function urlBase64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  return Uint8Array.from([...rawData].map((char) => char.charCodeAt(0)));
}

export default function PushNotificationButton() {
  const [isSubscribed, setIsSubscribed] = useState(false);

  useEffect(() => {
    const checkSubscription = async () => {
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) return;
      const registration = await navigator.serviceWorker.getRegistration('/sw.js');
      const subscription = await registration?.pushManager.getSubscription();
      setIsSubscribed(Boolean(subscription));
    };

    checkSubscription();
  }, []);

  const handleEnableNotifications = async () => {
    if (!('serviceWorker' in navigator) || !('PushManager' in window) || !('Notification' in window)) {
      alert('Le notifiche push non sono supportate su questo browser. Su iOS aggiungi prima l\'app alla schermata Home.');
      return false;
    }

    if (!VAPID_PUBLIC_KEY) {
      console.error('VITE_VAPID_PUBLIC_KEY mancante');
      return false;
    }

    try {
      const permission = await Notification.requestPermission();
      if (permission !== 'granted') return false;

      const registration = await navigator.serviceWorker.register('/sw.js');
      await navigator.serviceWorker.ready;

      const subscription = await registration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      });

      await api.post('/push/subscribe', subscription.toJSON());
      setIsSubscribed(true);
      return true;
    } catch (err) {
      console.error('Errore attivazione push:', err);
      return false;
    }
  };

  const handleDisableNotifications = async () => {
    try {
      const registration = await navigator.serviceWorker.getRegistration('/sw.js');
      const subscription = await registration?.pushManager.getSubscription();

      if (subscription) {
        await api.post('/push/unsubscribe', { endpoint: subscription.endpoint });
        await subscription.unsubscribe();
      }
      setIsSubscribed(false);
    } catch (err) {
      console.error('Errore disattivazione push:', err);
    }
  };

  return (
    <Toggle enableFunction={handleEnableNotifications} disableFunction={handleDisableNotifications} defaultStatus={isSubscribed}/>
  );
}