export type MaterialCategory = 'mandatory' | 'optional';

type Status = 'in_stock' | 'low' | 'out';

export interface Material {
  id: string;
  name: string;
  code: string;
  unit: string;
  quantity: number;
  status: Status;
  category: MaterialCategory;
  eta?: string;
}
