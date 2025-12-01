import { Material } from '@types/material';

export const mockMaterials: Material[] = [
  {
    id: 'oil-filter',
    name: 'Фильтр масляный TOR-400',
    code: 'TOR-400-FLTR',
    unit: 'шт',
    quantity: 6,
    status: 'in_stock',
    category: 'mandatory'
  },
  {
    id: 'hydraulic-fluid',
    name: 'Гидравлическая жидкость ISO VG 46',
    code: 'ISO-VG46',
    unit: 'л',
    quantity: 18,
    status: 'low',
    category: 'mandatory',
    eta: 'Доставка 12 дек'
  },
  {
    id: 'coolant',
    name: 'Охлаждающая жидкость TORO Coolant',
    code: 'TO-CLNT',
    unit: 'л',
    quantity: 0,
    status: 'out',
    category: 'mandatory',
    eta: 'Ожидается 15 дек'
  },
  {
    id: 'v-belt',
    name: 'Приводной ремень 12x1200',
    code: 'VB-12-1200',
    unit: 'шт',
    quantity: 9,
    status: 'in_stock',
    category: 'optional'
  }
];
