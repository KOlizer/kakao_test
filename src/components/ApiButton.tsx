// src/components/ApiButton.tsx
import React from 'react';
import { SharedButton } from './ButtonStyles';

interface ApiButtonProps {
    label: string;
    onClick: () => void;
}

const ApiButton: React.FC<ApiButtonProps> = ({ label, onClick }) => {
    return <SharedButton onClick={onClick}>{label}</SharedButton>;
};

export default ApiButton;
