import React from 'react';
import styled from 'styled-components';

const Button = styled.button`
  background-color: #dc3545;
  color: white;
  border: none;
  padding: 0.75em 1.5em;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  transition: all 0.001s ease-in;
  margin: 0 1em;

  &:hover {
    background-color: #c82333;
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 8px rgba(220, 53, 69, 0.6);
  }
`;

interface FormData {
  accessKey: string;
  secretKey: string;
  email: string;
  projectName: string;
  clusterList: string;
  clusterName: string;
  apiEndpoint: string;
  authData: string;
  instanceList: string;
  primaryEndpoint: string;
  standbyEndpoint: string;
  dockerImageName: string;
  dockerJavaVersion: string;
}

interface ValidateButtonProps {
  formData: FormData;
}

const ValidateButton: React.FC<ValidateButtonProps> = ({ formData }) => {
  const validate = () => {
    let isValid = true;
    const errors: string[] = [];

    console.log("Access Key:", formData.accessKey);
    console.log("Secret Key:", formData.secretKey);

    const accessKeyPattern = /^[a-f0-9]{32}$/;
    if (!formData.accessKey) {
      isValid = false;
      errors.push("사용자 액세스 키를 입력해주세요.");
    } else if (!accessKeyPattern.test(formData.accessKey)) {
      isValid = false;
      errors.push("사용자 액세스 키는 32자의 16진수여야 합니다.");
    }

    const secretKeyPattern = /^[a-f0-9]{70}$/;
    if (!formData.secretKey) {
      isValid = false;
      errors.push("사용자 액세스 보안 키를 입력해주세요.");
    } else if (!secretKeyPattern.test(formData.secretKey)) {
      isValid = false;
      errors.push("사용자 액세스 보안 키는 70자의 16진수여야 합니다.");
    }

    if (!formData.projectName) {
      isValid = false;
      errors.push("프로젝트 이름을 입력해주세요.");
      // + 이 부분에 프로젝트 중 하나 인지 검증하는 코드 추가
    }

    if (!formData.clusterName) {
      isValid = false;
      errors.push("클러스터 이름을 입력해주세요.");
      // + 이 부분에 클러스터 중 하나 인지 검사하는 코드 추가
    }

    const apiEndpointPattern = /^(https?:\/\/)?([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}(:\d{1,5})?(\/.*)?$/;
    if (!formData.apiEndpoint) {
      isValid = false;
      errors.push("클러스터의 API 엔드포인트를 입력해주세요.");
    } else if (!apiEndpointPattern.test(formData.apiEndpoint)) {
      isValid = false;
      errors.push("클러스터의 API 엔드포인트 형식이 올바르지 않습니다.");
    }

    const authDataPattern = /^[A-Za-z0-9+/=]{1428}$/;
    if (!formData.authData) {
      isValid = false;
      errors.push("클러스터의 certificate-authority-data를 입력해주세요.");
    } else if (!authDataPattern.test(formData.authData)) {
      isValid = false;
      errors.push("클러스터의 certificate-authority-data 형식이 올바르지 않습니다.");
    }

    const sqlendpointPattern = /^[a-z0-9-]+\.database\.[a-f0-9]{32}\.mysql\.managed-service\.[a-z0-9-]+\.[a-z]{2,}\.[a-z]{3}$/;
    if (!formData.primaryEndpoint) {
      isValid = false;
      errors.push("Primary의 엔드포인트를 입력해주세요.");
    } else if (!sqlendpointPattern.test(formData.primaryEndpoint)) {
      isValid = false;
      errors.push("Primary의 엔드포인트 형식이 올바르지 않습니다.");
    }

    if (!formData.standbyEndpoint) {
      isValid = false;
      errors.push("Standby의 엔드포인트를 입력해주세요.");
    } else if (!sqlendpointPattern.test(formData.standbyEndpoint)) {
      isValid = false;
      errors.push("Standby의 엔드포인트 형식이 올바르지 않습니다.");
    }


    if (!formData.dockerImageName) {
      isValid = false;
      errors.push("Docker Image 이름을 입력해주세요.");
    } else if (formData.dockerImageName !== "demo-spring-boot") {
      isValid = false;
      errors.push("Docker Image 이름은 'demo-spring-boot'이어야 합니다.");
    }

    if (!formData.dockerJavaVersion) {
      isValid = false;
      errors.push("Docker Image Base Java Version을 입력해주세요.");
    } else if (formData.dockerJavaVersion !== "17-jdk-slim") {
      isValid = false;
      errors.push("Docker Image Base Java Version은 '17-jdk-slim'이어야 합니다.");
    }

    if (isValid) {
      alert('검증 완료: 입력이 올바릅니다!');
    } else {
      alert(`Form has errors:\n${errors.join('\n')}`);
    }
  };

  return <Button onClick={validate}>유효성 검사</Button>;
};

export default ValidateButton;
