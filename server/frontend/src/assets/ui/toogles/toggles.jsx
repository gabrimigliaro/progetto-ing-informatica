import { useState, useEffect } from 'react';

import toggles from './toggles.module.css';

export default function Toggle({ enableFunction, disableFunction, defaultStatus = false }) {
    const [toggleState, setToggleState] = useState(defaultStatus)
    const [isBusy, setIsBusy] = useState(false);

    useEffect(() => {
        setToggleState(defaultStatus);
    }, [defaultStatus]);

    const changeToggleState = async () => {
        if (isBusy) return;
        setIsBusy(true);

        try {
            if (toggleState) {
                setToggleState(false)
                await disableFunction()
                
            } else {
                setToggleState(true)
                const success = await enableFunction();
                if (success === false) setToggleState(false)
            }
        } catch {
            setToggleState(toggleState);
        } finally {
            setIsBusy(false);
        }
    }

    return (
        <div onClick={changeToggleState} className={`${toggles.toggle} ${toggleState ? toggles.active : ''}`}>
            <div className={`${toggles.circle}`}></div>
        </div>
    );
}