/**
 * Settings Page
 * User and system configuration
 */

import { useState } from 'react';
import { User, Building2, Settings as SettingsIcon, Bell, Shield } from 'lucide-react';
import { MainLayout } from '@/components/layout/MainLayout';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card } from '@/components/ui/card';
import { ProfileTab } from '@/components/settings/ProfileTab';
import { NotaryConfigTab } from '@/components/settings/NotaryConfigTab';
import { PreferencesTab } from '@/components/settings/PreferencesTab';
import { SecurityTab } from '@/components/settings/SecurityTab';
import { NotificationsTab } from '@/components/settings/NotificationsTab';

type SettingsTab = 'profile' | 'notary' | 'preferences' | 'security' | 'notifications';

export function Settings() {
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold text-neutral-900">Configuración</h1>
          <p className="text-neutral-600 mt-1">
            Administra tu perfil, notaría y preferencias del sistema
          </p>
        </div>

        {/* Settings Tabs */}
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as SettingsTab)}>
          <TabsList className="flex w-full overflow-x-auto scrollbar-hide gap-1">
            <TabsTrigger value="profile" className="gap-2 flex-shrink-0">
              <User className="w-4 h-4" />
              <span className="hidden sm:inline">Perfil</span>
            </TabsTrigger>
            <TabsTrigger value="notary" className="gap-2 flex-shrink-0">
              <Building2 className="w-4 h-4" />
              <span className="hidden sm:inline">Notaría</span>
            </TabsTrigger>
            <TabsTrigger value="preferences" className="gap-2 flex-shrink-0">
              <SettingsIcon className="w-4 h-4" />
              <span className="hidden sm:inline">Preferencias</span>
            </TabsTrigger>
            <TabsTrigger value="security" className="gap-2 flex-shrink-0">
              <Shield className="w-4 h-4" />
              <span className="hidden sm:inline">Seguridad</span>
            </TabsTrigger>
            <TabsTrigger value="notifications" className="gap-2 flex-shrink-0">
              <Bell className="w-4 h-4" />
              <span className="hidden sm:inline">Notificaciones</span>
            </TabsTrigger>
          </TabsList>

          <Card className="mt-6">
            <TabsContent value="profile" className="p-4 sm:p-6">
              <ProfileTab />
            </TabsContent>

            <TabsContent value="notary" className="p-4 sm:p-6">
              <NotaryConfigTab />
            </TabsContent>

            <TabsContent value="preferences" className="p-4 sm:p-6">
              <PreferencesTab />
            </TabsContent>

            <TabsContent value="security" className="p-4 sm:p-6">
              <SecurityTab />
            </TabsContent>

            <TabsContent value="notifications" className="p-4 sm:p-6">
              <NotificationsTab />
            </TabsContent>
          </Card>
        </Tabs>
      </div>
    </MainLayout>
  );
}
