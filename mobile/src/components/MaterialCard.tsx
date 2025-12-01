import React, { FC, useMemo } from 'react';
import styled from 'styled-components/native';

import { colors, radii, spacing } from '@theme/index';
import { Material } from '@types/material';

interface Props {
  material: Material;
}

const statusMap = {
  in_stock: { label: 'На складе', color: colors.success, bg: 'rgba(52, 199, 89, 0.15)' },
  low: { label: 'Заканчивается', color: colors.warning, bg: 'rgba(242, 120, 28, 0.15)' },
  out: { label: 'Нет в наличии', color: colors.primary, bg: colors.primaryMuted }
} as const;

const categoryMap = {
  mandatory: 'Критично для ТО',
  optional: 'Опционально'
} as const;

export const MaterialCard: FC<Props> = ({ material }) => {
  const status = statusMap[material.status];

  // Keep the quantity color in sync with the current stock status.
  const quantityColor = useMemo(() => {
    if (material.status === 'out') return colors.textMuted;
    if (material.status === 'low') return colors.warning;
    return colors.textPrimary;
  }, [material.status]);

  return (
    <Card>
      <Header>
        <Title>{material.name}</Title>
        <StatusPill background={status.bg}>
          <StatusText color={status.color}>{status.label}</StatusText>
        </StatusPill>
      </Header>

      <Meta>
        <MetaLabel>Категория</MetaLabel>
        <MetaValue>{categoryMap[material.category]}</MetaValue>
      </Meta>

      <Divider />

      <Row>
        <Cell>
          <MetaLabel>Код</MetaLabel>
          <MetaValue>{material.code}</MetaValue>
        </Cell>
        <Cell>
          <MetaLabel>Ед. изм.</MetaLabel>
          <MetaValue>{material.unit}</MetaValue>
        </Cell>
        <Cell>
          <MetaLabel>Количество</MetaLabel>
          <Quantity style={{ color: quantityColor }}>{material.quantity}</Quantity>
        </Cell>
      </Row>

      {material.eta ? (
        <Alert>
          <AlertDot />
          <AlertText>{material.eta}</AlertText>
        </Alert>
      ) : (
        <Spacer />
      )}
    </Card>
  );
};

const Card = styled.View`
  background-color: ${colors.surface};
  border-radius: ${radii.lg}px;
  padding: ${spacing.lg}px;
  gap: ${spacing.md}px;
  shadow-color: rgba(16, 24, 40, 0.12);
  shadow-offset: 0px 10px;
  shadow-opacity: 0.18;
  shadow-radius: 30px;
  elevation: 5;
`;

const Header = styled.View`
  flex-direction: row;
  justify-content: space-between;
  align-items: flex-start;
  gap: ${spacing.sm}px;
`;

const Title = styled.Text`
  flex: 1;
  font-weight: 600;
  font-size: 16px;
  line-height: 22px;
  color: ${colors.textPrimary};
`;

const StatusPill = styled.View<{ background: string }>`
  padding: ${spacing.xs}px ${spacing.md}px;
  border-radius: 999px;
  background-color: ${({ background }) => background};
`;

const StatusText = styled.Text<{ color: string }>`
  font-size: 12px;
  font-weight: 600;
  color: ${({ color }) => color};
`;

const Meta = styled.View`
  flex-direction: row;
  justify-content: space-between;
`;

const MetaLabel = styled.Text`
  font-size: 12px;
  color: ${colors.textMuted};
`;

const MetaValue = styled.Text`
  font-size: 13px;
  color: ${colors.textPrimary};
  font-weight: 500;
`;

const Divider = styled.View`
  height: 1px;
  background-color: ${colors.border};
`;

const Row = styled.View`
  flex-direction: row;
  gap: ${spacing.md}px;
`;

const Cell = styled.View`
  flex: 1;
`;

const Quantity = styled.Text`
  font-size: 18px;
  font-weight: 600;
`;

const Alert = styled.View`
  flex-direction: row;
  align-items: center;
  gap: ${spacing.xs}px;
  padding: ${spacing.xs}px 0;
`;

const AlertDot = styled.View`
  width: 8px;
  height: 8px;
  border-radius: 4px;
  background-color: ${colors.warning};
`;

const AlertText = styled.Text`
  font-size: 12px;
  color: ${colors.warning};
  font-weight: 500;
`;

const Spacer = styled.View`
  height: ${spacing.xs}px;
`;
