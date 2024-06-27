// src/components/ApiButton.tsx
import React from 'react';
import styled from 'styled-components';

interface ApiButtonProps {
    label: string;
    onClick: () => void;
}

const Button = styled.button`
    background-color: #e9e445;
    color: #000;
    border: none;
    padding: 0.3em 1em;
    border-radius: 20px;
    cursor: pointer;
    font-size: 0.85em;
    transition: all 0.3s ease;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    margin-top: -0.5em; // 인풋 박스 위로 위치 조정
    display: inline;

    &:hover {
        background-color: #ffce00;
    }

    &:focus {
        outline: none;
        box-shadow: 0 0 8px rgba(255, 206, 0, 0.6);
    }
`;

const ApiButton: React.FC<ApiButtonProps> = ({ label, onClick }) => {
    return <Button onClick={onClick}>{label}</Button>;
};

export default ApiButton;
