import React from 'react';
import { Combobox, useCombobox, InputBase, Loader } from '@mantine/core';
import styled from 'styled-components';
import { useChat } from '../context/ChatContext';
import customLogoUrl from '../assets/images/custom_logo.png';

const SelectorContainer = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Logo = styled.img`
  width: 32px;
  height: 32px;
  object-fit: contain;
`;

const ErrorText = styled.span`
  color: #dc3545;
  font-size: 12px;
`;

const EndpointSelector: React.FC = () => {
  const { 
    servingEndpoints, 
    selectedEndpoint, 
    setSelectedEndpoint, 
    endpointsLoading, 
    endpointsError 
  } = useChat();
  
  const combobox = useCombobox({
    onDropdownClose: () => combobox.resetSelectedOption(),
  });

  const options = servingEndpoints.map((endpoint) => (
    <Combobox.Option 
      value={endpoint.name} 
      key={endpoint.name}
      aria-label={`Select endpoint ${endpoint.name}`}
    >
      {endpoint.name}
    </Combobox.Option>
  ));

  if (endpointsError) {
    return (
      <SelectorContainer>
        <Logo src={customLogoUrl} alt="App Logo" />
        <ErrorText>{endpointsError}</ErrorText>
      </SelectorContainer>
    );
  }

  return (
    <SelectorContainer>
      <Logo src={customLogoUrl} alt="App Logo" />
      <Combobox
        store={combobox}
        onOptionSubmit={(val) => {
          setSelectedEndpoint(val);
          combobox.closeDropdown();
        }}
      >
        <Combobox.Target>
          <InputBase
            component="button"
            type="button"
            pointer
            rightSection={endpointsLoading ? <Loader size={16} /> : <Combobox.Chevron />}
            rightSectionPointerEvents="none"
            onClick={() => combobox.toggleDropdown()}
            aria-label="Select serving endpoint"
            aria-expanded={combobox.dropdownOpened}
            aria-haspopup="listbox"
            styles={{
              input: {
                minWidth: '200px',
                border: '1px solid #C0CDD8',
                borderRadius: '4px',
                fontSize: '13px',
                padding: '6px 12px',
                height: '32px',
                cursor: 'pointer',
                '&:hover': {
                  borderColor: '#2272B4',
                },
                '&:focus': {
                  borderColor: '#2272B4',
                  outline: 'none',
                },
              },
            }}
          >
            {selectedEndpoint || (endpointsLoading ? 'Loading...' : 'Select endpoint')}
          </InputBase>
        </Combobox.Target>

        <Combobox.Dropdown>
          <Combobox.Options aria-label="Available serving endpoints">
            {options.length > 0 ? options : (
              <Combobox.Empty>No endpoints available</Combobox.Empty>
            )}
          </Combobox.Options>
        </Combobox.Dropdown>
      </Combobox>
    </SelectorContainer>
  );
};

export default EndpointSelector;
