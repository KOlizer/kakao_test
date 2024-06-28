// src/components/ApiButton.tsx
import React from 'react';
import { SharedButton } from './ButtonStyles';
import styled from 'styled-components';

interface ApiButtonProps {
    label: string;
    onClick: () => void;
    isLoading: boolean;
}

const Loader = styled.div`
    border: 4px solid rgba(255, 255, 255, 0.3);
    border-radius: 50%;
    border-top: 4px solid #fff;
    width: 16px;
    height: 16px;
    animation: spin 2s linear infinite;

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;

const ApiButton: React.FC<ApiButtonProps> = ({ label, onClick, isLoading }) => {
    return (
        <SharedButton onClick={onClick} disabled={isLoading}>
            {isLoading ? <Loader /> : label}
        </SharedButton>
    );
};

export default ApiButton;
