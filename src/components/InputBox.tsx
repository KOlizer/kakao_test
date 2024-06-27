// src/components/InputBox.tsx
import React from 'react';
import styled from 'styled-components';
import ApiButton from "components/ApiButton";

interface InputBoxProps {
    label: string;
    placeholder: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    height?: string;
}

const Container = styled.div`
    margin-bottom: 2.5em;
    width: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: inherit; // Button 요소를 우상단에 정렬
    position: relative;
`;

const LabelContainer = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
`;

const Label = styled.label`
    display: inline;
    margin-bottom: 0.5em;
    margin-right: 1em;
    font-weight: bold;
    color: white;
`;

const Input = styled.input<{ height?: string }>`
    width: 100%;
    padding: 0.75em;
    border: 1px solid #ccc;
    border-radius: 4px;
    transition: all 0.3s ease;
    height: ${(props) => props.height || 'auto'};

    &:focus {
        border-color: #007bff;
        box-shadow: 0 0 8px rgba(0, 123, 255, 0.2);
        outline: none;
    }
`;

const InputBox: React.FC<InputBoxProps> = ({ label, placeholder, value, onChange, height }) => {
    return (
        <Container>
            <LabelContainer>
                <Label>{label}</Label>
                <ApiButton label="API로 조회" onClick={() => {/* API 호출 로직 추가 */}} />
            </LabelContainer>
            <Input type="text" placeholder={placeholder} value={value} onChange={onChange} height={height} />
        </Container>
    );
};

export default InputBox;
