import React from 'react';
import styles from './Spinner.module.css';

export const Spinner = () => {
  return (
    <div className={styles.spinnerContainer}>
      <div className={styles.dot}></div>
      <div className={styles.dot}></div>
      <div className={styles.dot}></div>
    </div>
  );
};
