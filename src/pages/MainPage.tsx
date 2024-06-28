// src/pages/MainPage.tsx
import React, { useState } from 'react';
import InputBox from '../components/InputBox';
import ScriptDisplay from '../components/ScriptDisplay';
import CopyButton from '../components/CopyButton';
import styled from 'styled-components';
import axios from 'axios';

const Container = styled.div`
    max-width: 800px;
    margin: 2em auto;
    padding: 2em;
    background-color: rgba(0, 0, 0, 0.5);
    border-radius: 8px;
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    z-index: 10;
    min-height: 100vh; // 컨테이너 높이를 최소 100vh로 설정
`;

const Title = styled.h1`
    text-align: center;
    margin-bottom: 1.5em;
    color: #fff;
`;

const GroupContainer = styled.div`
    margin-bottom: 2em;
    padding: 1em;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 8px;
`;

const ButtonContainer = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 2em;
`;

const StyledButton = styled.button`
    background-color: #28a745;
    color: white;
    border: none;
    padding: 0.75em 1.5em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1em;
    transition: background-color 0.1s ease-in;
    margin: 0 1em;

    &:hover {
        background-color: #218838;
    }

    &:focus {
        outline: none;
        box-shadow: 0 0 8px rgba(33, 136, 56, 0.6);
    }
`;

const MainPage: React.FC = () => {
    const [accessKey, setAccessKey] = useState('');
    const [secretKey, setSecretKey] = useState('');
    const [email, setEmail] = useState('');
    const [projectName, setProjectName] = useState('');
    const [clusterList, setClusterList] = useState('');
    const [clusterName, setClusterName] = useState('');
    const [apiEndpoint, setApiEndpoint] = useState('');
    const [authData, setAuthData] = useState('');
    const [instanceList, setInstanceList] = useState('');
    const [primaryEndpoint, setPrimaryEndpoint] = useState('');
    const [standbyEndpoint, setStandbyEndpoint] = useState('');
    const [dockerImageName, setDockerImageName] = useState('demo-spring-boot');
    const [dockerJavaVersion, setDockerJavaVersion] = useState('17-jdk-slim');
    const [script, setScript] = useState('');

    const generateScript = () => {
        const newScript = `#!/bin/bash
echo "kakaocloud: 1.Starting environment variable setup"
# 환경 변수 설정: 사용자는 이 부분에 자신의 환경에 맞는 값을 입력해야 합니다.
command=$(cat <<EOF
export ACC_KEY='${accessKey}'
export SEC_KEY='${secretKey}'
export EMAIL_ADDRESS='${email}'
export CLUSTER_NAME='${clusterName}'
export API_SERVER='${apiEndpoint}'
export AUTH_DATA='${authData}'
export PROJECT_NAME='${projectName}'
export INPUT_DB_EP1='${primaryEndpoint}'
export INPUT_DB_EP2='${standbyEndpoint}'
export DOCKER_IMAGE_NAME='${dockerImageName}'
export DOCKER_JAVA_VERSION='${dockerJavaVersion}'
export JAVA_VERSION='17'
export SPRING_BOOT_VERSION='3.1.0'
export DB_EP1=\$(echo -n "\$INPUT_DB_EP1" | base64 -w 0)
export DB_EP2=\$(echo -n "\$INPUT_DB_EP2" | base64 -w 0)
EOF
)
eval "$command"
echo "$command" >> /home/ubuntu/.bashrc
echo "kakaocloud: Environment variable setup completed"
echo "kakaocloud: 2.Checking the validity of the script download site"
curl --output /dev/null --silent --head --fail "https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/script/script.sh" || { echo "kakaocloud: Script download site is not valid"; exit 1; }
echo "kakaocloud: Script download site is valid"
wget https://github.com/kakaocloud-edu/tutorial/raw/main/AdvancedCourse/src/script/script.sh
chmod +x script.sh
sudo -E ./script.sh`;
        setScript(newScript);
    };

    // API 조회 함수
    const handleApiClick = async (url: string, setter: (data: string) => void) => {
        try {
            const response = await axios.get(url);
            setter(response.data);
        } catch (error) {
            console.error('API 호출 오류:', error);
        }
    };

    // 콘솔로 조회 버튼 핸들러
    const handleConsoleClick = (url: string) => {
        window.open(url, '_blank');
    };

    return (
        <Container>
            <Title>Bastion VM 스크립트 생성</Title>
            <GroupContainer>
                <InputBox label="사용자 액세스 키" placeholder="직접 입력" value={accessKey} onChange={(e) => setAccessKey(e.target.value)} />
                <InputBox label="사용자 액세스 보안 키" placeholder="직접 입력" value={secretKey} onChange={(e) => setSecretKey(e.target.value)} />
                <InputBox label="사용자 이메일" placeholder="직접 입력" value={email} onChange={(e) => setEmail(e.target.value)} />
            </GroupContainer>
            <GroupContainer>
                <InputBox
                    label="프로젝트 이름"
                    placeholder="직접 입력"
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    showApiButton
                    onApiClick={() => handleApiClick('API_ENDPOINT_FOR_PROJECT_NAME', setProjectName)} // 실제 API 엔드포인트로 대체
                    onConsoleClick={() => handleConsoleClick('https://github.com/your-repo/your-project')} // GitHub 링크로 대체
                />
            </GroupContainer>
            <GroupContainer>
                <InputBox
                    label="클러스터 리스트"
                    placeholder="직접 입력"
                    value={clusterList}
                    onChange={(e) => setClusterList(e.target.value)}
                    height="100px"
                    showApiButton
                    onApiClick={() => handleApiClick('API_ENDPOINT_FOR_CLUSTER_LIST', setClusterList)} // 실제 API 엔드포인트로 대체
                    onConsoleClick={() => handleConsoleClick('https://github.com/your-repo/your-project')} // GitHub 링크로 대체
                />
                <InputBox label="클러스터 이름" placeholder="직접 입력" value={clusterName} onChange={(e) => setClusterName(e.target.value)} />
                <InputBox label="클러스터의 API 엔드포인트" placeholder="직접 입력" value={apiEndpoint} onChange={(e) => setApiEndpoint(e.target.value)} />
                <InputBox label="클러스터의 certificate-authority-data" placeholder="직접 입력" value={authData} onChange={(e) => setAuthData(e.target.value)} />
            </GroupContainer>
            <GroupContainer>
                <InputBox
                    label="인스턴스 리스트"
                    placeholder="직접 입력"
                    value={instanceList}
                    onChange={(e) => setInstanceList(e.target.value)}
                    height="100px"
                    showApiButton
                    onApiClick={() => handleApiClick('API_ENDPOINT_FOR_INSTANCE_LIST', setInstanceList)} // 실제 API 엔드포인트로 대체
                    onConsoleClick={() => handleConsoleClick('https://github.com/your-repo/your-project')} // GitHub 링크로 대체
                />
                <InputBox label="Primary의 엔드포인트" placeholder="직접 입력" value={primaryEndpoint} onChange={(e) => setPrimaryEndpoint(e.target.value)} />
                <InputBox label="Standby의 엔드포인트" placeholder="직접 입력" value={standbyEndpoint} onChange={(e) => setStandbyEndpoint(e.target.value)} />
            </GroupContainer>
            <GroupContainer>
                <InputBox label="Docker Image 이름" placeholder="직접 입력" value={dockerImageName} onChange={(e) => setDockerImageName(e.target.value)} />
                <InputBox label="Docker Image Base Java Version" placeholder="직접 입력" value={dockerJavaVersion} onChange={(e) => setDockerJavaVersion(e.target.value)} />
            </GroupContainer>
            <ButtonContainer>
                <StyledButton onClick={generateScript}>스크립트 생성</StyledButton>
                <CopyButton script={script} />
            </ButtonContainer>
            <ScriptDisplay script={script} />
        </Container>
    );
};

export default MainPage;
