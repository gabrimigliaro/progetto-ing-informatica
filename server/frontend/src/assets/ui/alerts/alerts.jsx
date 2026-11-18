import alerts from './alerts.module.css';

const ALERT_TYPES = {
    success: {
        className: alerts.green,
    },

    error: {
        className: alerts.red,
    },

    warning: {
        className: alerts.yellow,
    },
};

export default function Alert({ type, text }) {
    const config = ALERT_TYPES[type];

    return (
        <div className={`${alerts.alert} ${config.className} center`}>
            <p className='text-xs'>{text}</p>
        </div>
    );
}