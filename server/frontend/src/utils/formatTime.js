export const formatTimeAgo = (createdAt, shortFormat = false) => {
    if (!createdAt) return '';

    const createdDate = new Date(createdAt);
    const now = new Date();
    const diffInMs = now - createdDate;

    if (isNaN(diffInMs) || diffInMs < 0) return shortFormat ? 'ora' : 'proprio ora';

    const diffInMinutes = Math.floor(diffInMs / (1000 * 60));
    const diffInHours = Math.floor(diffInMinutes / 60);
    const diffInDays = Math.floor(diffInHours / 24);

    if (diffInHours < 1) {
        const mins = diffInMinutes === 0 ? 1 : diffInMinutes;
        return shortFormat ? `${mins}m` : `${mins} min`;
    }

    if (diffInDays < 1) {
        return shortFormat 
        ? `${diffInHours}h` 
        : `${diffInHours} ${diffInHours === 1 ? 'ora' : 'ore'}`;
    }

    return shortFormat 
        ? `${diffInDays}g` 
        : `${diffInDays} ${diffInDays === 1 ? 'giorno' : 'giorni'}`;
};

export const formatDateTime = (isoString) => {
    if (!isoString) return '-';

    const date = new Date(isoString);
    
    if (isNaN(date.getTime())) return '-';

    const datePart = date.toLocaleDateString('it-IT', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
    });

    const timePart = date.toLocaleTimeString('it-IT', {
        hour: '2-digit',
        minute: '2-digit',
    });

    return `${datePart} alle ${timePart}`;
};