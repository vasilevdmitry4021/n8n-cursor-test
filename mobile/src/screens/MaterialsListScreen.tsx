import React, { FC, useMemo, useState } from 'react';
import { FlatList, ListRenderItemInfo, StatusBar } from 'react-native';
import styled from 'styled-components/native';

import { MaterialCard } from '@components/MaterialCard';
import { mockMaterials } from '@constants/materials';
import { colors, radii, spacing } from '@theme/index';
import { Material, MaterialCategory } from '@types/material';

const filters: Array<{ id: MaterialCategory | 'all'; label: string }> = [
  { id: 'all', label: 'Все' },
  { id: 'mandatory', label: 'Обязательные' },
  { id: 'optional', label: 'Опциональные' }
];

export const MaterialsListScreen: FC = () => {
  const [query, setQuery] = useState('');
  const [filter, setFilter] = useState<(typeof filters)[number]['id']>('all');

  // Derive filtered list once per render to avoid recomputation in FlatList callbacks.
  const filteredMaterials = useMemo(() => {
    return mockMaterials.filter((material) => {
      const matchesCategory = filter === 'all' ? true : material.category === filter;
      const matchesQuery = material.name.toLowerCase().includes(query.toLowerCase());
      return matchesCategory && matchesQuery;
    });
  }, [filter, query]);

  const renderItem = ({ item }: ListRenderItemInfo<Material>) => <MaterialCard material={item} />;

  const keyExtractor = (item: Material) => item.id;

  return (
    <Screen>
      <StatusBar barStyle="dark-content" backgroundColor={colors.background} />
      <SafeArea>
        <Header>
          <Title>Материалы для ТОРО</Title>
          <Subtitle>Обновлено сегодня, 12:30</Subtitle>
        </Header>

        <SearchField
          placeholder="Поиск по названию"
          value={query}
          onChangeText={setQuery}
          autoCorrect={false}
          testID="materials-search"
        />

        <Filters>
          {filters.map(({ id, label }) => {
            const isActive = filter === id;
            return (
              <FilterChip key={id} active={isActive} onPress={() => setFilter(id)}>
                <FilterText active={isActive}>{label}</FilterText>
              </FilterChip>
            );
          })}
        </Filters>

        <FlatList
          data={filteredMaterials}
          keyExtractor={keyExtractor}
          renderItem={renderItem}
          showsVerticalScrollIndicator={false}
          ItemSeparatorComponent={Separator}
          contentContainerStyle={{ paddingBottom: spacing.xxl }}
          ListEmptyComponent={<EmptyState>Материалы не найдены</EmptyState>}
        />
      </SafeArea>
    </Screen>
  );
};

const Screen = styled.View`
  flex: 1;
  background-color: ${colors.background};
`;

const SafeArea = styled.SafeAreaView`
  flex: 1;
  padding: ${spacing.xxl}px ${spacing.xl}px;
  gap: ${spacing.lg}px;
`;

const Header = styled.View`
  gap: ${spacing.xs}px;
`;

const Title = styled.Text`
  font-size: 22px;
  font-weight: 700;
  color: ${colors.textPrimary};
`;

const Subtitle = styled.Text`
  font-size: 13px;
  color: ${colors.textSecondary};
`;

const SearchField = styled.TextInput.attrs({
  placeholderTextColor: colors.textMuted
})`
  padding: ${spacing.sm}px ${spacing.md}px;
  border-radius: ${radii.lg}px;
  border-width: 1px;
  border-color: ${colors.border};
  background-color: ${colors.surface};
  font-size: 14px;
`;

const Filters = styled.View`
  flex-direction: row;
  flex-wrap: wrap;
  gap: ${spacing.sm}px;
`;

const FilterChip = styled.Pressable<{ active: boolean }>`
  padding: ${spacing.xs}px ${spacing.md}px;
  border-radius: 999px;
  border-width: 1px;
  border-color: ${({ active }) => (active ? colors.primary : colors.border)};
  background-color: ${({ active }) => (active ? colors.primaryMuted : colors.surface)};
`;

const FilterText = styled.Text<{ active: boolean }>`
  font-size: 13px;
  font-weight: 600;
  color: ${({ active }) => (active ? colors.primary : colors.textSecondary)};
`;

const Separator = styled.View`
  height: ${spacing.md}px;
`;

const EmptyState = styled.Text`
  text-align: center;
  margin-top: ${spacing.xl}px;
  color: ${colors.textMuted};
`;
